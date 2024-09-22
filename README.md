# EDI Converter

## Description

Le **EDI Converter** est un utilitaire Python permettant de convertir des fichiers au format EDI (Electronic Data Interchange) en fichiers CSV avec un format prédéfini. Ce projet est principalement conçu pour traiter et transformer des données de consommation énergétique ou d'échange électronique de données provenant de différents systèmes en une structure tabulaire lisible.

### Fonctionnalités principales :
- Lecture de fichiers EDI et extraction des informations pertinentes.
- Conversion de ces données en fichiers CSV.
- Vérification de la validité des données lors de la conversion.

## Structure du projet

- **constants.py** : Contient les constantes (délimiteurs CSV, préfixes, etc.).
- **exceptions.py** : Gère les exceptions personnalisées, notamment `EntryHeaderCSVConflict`.
- **helpers.py** : Contient des fonctions utilitaires comme `gen_file_name`.
- **logger.py** : Configuration d’un logger personnalisé pour tracer l'exécution du programme.

## Fonctionnalités

### 1. Conversion EDI vers CSV
La méthode `to_csv` convertit les données extraites d'un fichier EDI en fichiers CSV en respectant un format prédéfini. Le processus comprend :
- Extraction des données EDI depuis des sections spécifiques.
- Gestion des formats et symboles particuliers comme les séparateurs de composants, d'éléments, et les dates au format `303`.
- Validation de la structure de chaque ligne CSV avant l'enregistrement.

### 2. Parsing des fichiers EDI
La méthode `parse_edi` permet de lire un fichier EDI et d'extraire les données dans un format structuré (dictionnaire Python). Le processus gère :
- Les sections LOC pour les emplacements.
- Les sections QTY pour les quantités.
- Les sections DTM pour les périodes temporelles.

### 3. Vérification des entrées CSV
La méthode `__verify_single_entry` compare chaque ligne CSV générée avec les en-têtes pour s'assurer que la structure est conforme et cohérente. Si une incohérence est détectée, une exception est levée.

## Utilisation

1. Cloner ce dépôt.
2. Configurer votre environnement Python et installer les dépendances.
3. Placer les fichiers EDI dans un répertoire cible.
4. Utiliser la classe `EDIConverter` pour lire les fichiers EDI et les convertir en CSV.

## Exemple de code

```python
from edi_converter import EDIConverter
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

# Initialisation du convertisseur
converter = EDIConverter(target_dir='/path/to/output/', logger=logger)

# Conversion d'un fichier EDI
converter.convert_to_csv('/path/to/edi/file.edi', ['Header1', 'Header2', 'Header3'])
