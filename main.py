import argparse
import os
import time
import re
import logging
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import Optional

import requests
from bs4 import BeautifulSoup
import boto3

# ==========================
# Data Model
# ==========================
@dataclass
class CreatureData:
    index: int
    name: str
    url: str
    image_url: Optional[str] = None

# ==========================
# Web Scraper
# ==========================
class WebScraper:
    def __init__(self, base_url: str, delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> BeautifulSoup:
        response = self.session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def extract_creature_data(self, element) -> Optional[CreatureData]:
        cells = element.find_all("td")
        if len(cells) < 3:
            return None
        
        index_match = re.search(r"\d+", cells[0].get_text(strip=True))
        if not index_match:
            return None

        link_element = element.find("a", href=True)
        if not link_element:
            return None

        return CreatureData(
            index=int(index_match.group()),
            name=link_element.get_text(strip=True),
            url=urljoin(self.base_url, link_element["href"])
        )

# ==========================
# Image Downloader
# ==========================
class ImageDownloader:
    def __init__(self, output_dir: str = "collected_data"):
        self.mode = os.getenv("STORAGE_MODE", "local")  # "local" ou "s3"
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        if self.mode == "s3":
            self.s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION", "eu-west-3"))
            self.bucket = os.getenv("S3_BUCKET")
            self.prefix = os.getenv("S3_PREFIX", "images")

    def save_image(self, url: str, filename: str) -> bool:
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            if self.mode == "local":
                # Sauvegarde locale
                with open(filename, "wb") as f:
                    f.write(response.content)
                logging.info(f"Saved locally: {filename}")
                return True

            elif self.mode == "s3":
                # Sauvegarde sur S3
                ext = os.path.splitext(urlparse(url).path)[-1] or ".png"
                key = f"{self.prefix}/{filename}{ext}"

                self.s3.put_object(Bucket=self.bucket, Key=key, Body=response.content)

                object_url = f"https://{self.bucket}.s3.eu-west-3.amazonaws.com/{key}"
                logging.info(f"Uploaded to S3: {object_url}")
                return True

        except Exception as e:
            logging.error(f"Failed to download/upload {url}: {e}")
            return False

# ==========================
# Data Collector
# ==========================
class DataCollector:
    def __init__(self):
        self.base_url = "https://bulbapedia.bulbagarden.net"
        self.list_url = f"{self.base_url}/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
        self.scraper = WebScraper(self.base_url)
        self.downloader = ImageDownloader()

    def find_creature_image(self, url: str) -> Optional[str]:
        try:
            soup = self.scraper.fetch_page(url)
            info_table = soup.find("table", {"class": re.compile(r"infobox|roundy")})
            if not info_table:
                return None
            img_tag = info_table.find("img")
            if not img_tag or not img_tag.get("src"):
                return None
            src = img_tag["src"]
            return f"https:{src}" if src.startswith("//") else src
        except Exception:
            return None

    def collect_data(self, limit: int = 5):
        soup = self.scraper.fetch_page(self.list_url)
        tables = soup.find_all("table", {"class": re.compile(r"(roundy|sortable)")})

        count = 0  # compteur de Pokémon traités

        for table in tables:
            for row in table.find_all("tr"):
                if count >= limit:
                    logging.info(f"Limit of {limit} Pokémon reached. Stopping.")
                    return

                creature = self.scraper.extract_creature_data(row)
                if not creature:
                    continue

                logging.info(f"Processing #{creature.index:04d} {creature.name}")
                
                image_url = self.find_creature_image(creature.url)
                if not image_url:
                    logging.warning(f"No image found for {creature.name}")
                    continue

                filename = f"{creature.index:04d}_{creature.name}"
                
                if self.downloader.save_image(image_url, filename):
                    logging.info(f"OK: {filename}")
                
                count += 1
                time.sleep(self.scraper.delay)

# ==========================
# Main Entry Point
# ==========================
def main():
    parser = argparse.ArgumentParser(description="Pokémon Image Scraper")
    parser.add_argument("--limit", type=int, default=5, help="Nombre maximum de Pokémon à scraper")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, 
                       format="%(asctime)s - %(levelname)s - %(message)s")
    
    collector = DataCollector()
    collector.collect_data(limit=args.limit)

if __name__ == "__main__":
    main()
