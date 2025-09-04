Poké Scraper – Rapport de projet

Objectif
Développer un scraper Python exécuté sur AWS EC2 pour collecter les images de Pokémon depuis Bulbapedia et les stocker dans un bucket S3, en respectant les bonnes pratiques de sécurité et de robustesse.

Architecture mise en place

EC2 Instance (Amazon Linux 2) : exécute le script Python.

IAM Role : associé à l’EC2 pour autoriser uniquement l’accès au bucket S3 sans stocker de clés AWS dans le code.

S3 Bucket : stockage des images, organisées sous le préfixe images/. Les objets sont publics pour visualisation directe via URL.

Flux de données

L’EC2 récupère la page listant tous les Pokémon sur Bulbapedia.

Extraction des URLs des images à l’aide de BeautifulSoup.

Téléchargement des images via requests.

Upload direct dans le bucket S3 via boto3.

Choix techniques

Python 3 : pour le scraping et la manipulation HTTP.

BeautifulSoup4 + requests : extraction HTML et téléchargement sécurisé.

Boto3 : interface avec AWS S3.

IAM Role + policies limitées : sécurité maximale, pas de clés en dur.

Gestion des erreurs réseau et images manquantes via try/except.

Respect des délais (time.sleep) pour ne pas surcharger Bulbapedia.

Résultats et tests

Test de 5 Pokémon initialement, puis extension à l’ensemble du Pokédex.

Vérification que les fichiers sont bien présents dans S3 et accessibles via URL publique.

Logs confirmant le succès de chaque téléchargement et upload.
