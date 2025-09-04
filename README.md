# Poké Scraper

## Description

Poké Scraper est un script Python conçu pour collecter les images de Pokémon depuis Bulbapedia et les stocker dans un bucket Amazon S3. Le projet est exécuté sur une instance EC2 et utilise des bonnes pratiques de sécurité et de robustesse, notamment en évitant le stockage de clés AWS dans le code.

## Objectif

- Scraper automatiquement les images de tous les Pokémon
- Stocker les images dans un bucket S3 avec un accès public
- Garantir la sécurité et la fiabilité du processus via IAM Roles et gestion d’erreurs

## Architecture

- **EC2 Instance (Amazon Linux 2)**  
  - Exécute le script Python

- **IAM Role**  
  - Attaché à l’EC2 pour autoriser uniquement l’accès au bucket S3, sans clés AWS en dur

- **S3 Bucket**  
  - Stocke les images sous le préfixe `images/`  
  - Les objets sont accessibles publiquement via URL

### Flux de données

- L’EC2 récupère la page listant tous les Pokémon sur Bulbapedia
- Extraction des URLs des images à l’aide de BeautifulSoup
- Téléchargement des images via requests
- Upload direct dans le bucket S3 via boto3

## Choix techniques

- **Python 3** : traitement HTTP et manipulation des données
- **BeautifulSoup4 + requests** : extraction HTML et téléchargement sécurisé
- **Boto3** : interface avec AWS S3
- **IAM Role + policies limitées** : sécurité maximale sans stocker de clés dans le code
- **Gestion des erreurs** : `try/except` pour les problèmes réseau ou images manquantes
- **Respect des délais** : `time.sleep()` pour éviter de surcharger Bulbapedia

Le script :
- **Scrape les images depuis Bulbapedia
- **Télécharge et envoie les images vers le bucket S3
- **Log chaque étape pour vérification

## Résultats et tests

- **Test initial sur 5 Pokémon puis extension à l’ensemble du Pokédex
- **Vérification que les fichiers sont bien présents dans S3 et accessibles via URL publique
- **Logs confirmant le succès de chaque téléchargement et upload
