# extractionCatalogs
<div align="justify">
Pour cette première version du programme d'extraction des catalogues d'exposition, j'ai travaillé sur les catalogues de type "simple". Il s'agit de catalogues dont les entrées sont structurées par ligne. Chaque ligne contient un élément bien distinct: auteur, informations biographiques, titre d'une oeuvre et potentielle informations supplémentaires sur l'oeuvre.
   <br/><br/>
<p align="center">
  <img src="./images/Exemple_Entree_Simple.png" width=400/>
 </p>
 <i>Image: Catalogue de l'exposition du musée des beaux arts de Rouen, 1860, p.24</i>
 <br/><br/>
  
 Je me suis pour l'instant concentrée sur les catalogues dont les entrées ont été bien reconnues par le segmenteur. L'idée serait par la suite d'utiliser un test, test_entree.py, disponible dans le dossier tests afin de déterminer si le résultat de l'ocr permet de réaliser ce travail en s'appuyant sur ces zones. 
 Un second test testValidationXml.py permet de vérifier si le document xml produit correspond bien à l'ODD réalisé par Caroline Corbières.
 Le TeiHeader est produit automatiquement et nécessite l'élaboration de questions afin de le remplir.
   
   <p align="center">
      <img src= "./images/pipeline_catalogue_extraction.png" width=400/>
   </p>
   <i>Image: Pipeline d'extraction des données des catalogues d'exposition</i>
 </div>
 
## How to use the repository
  - Clone the repository: ```git clone https://github.com/Juliettejns/extractionCatalogs```
  - Create virtual environment: ```virtualenv -p python3 env```
  - Run the virtual env: ```source env/bin/activate```
  - Install the requirements: ```pip install -r requirements.txt```
  - Run the program: ```python3 run.py```
  - Stop the virtual env: ```source env/bin/deactivate```

## Repository
```
├── fichiers_test
│     └── data test (alto 4 xml, Kraken output)
|
├─ fonctions
|     ├─ creationTeiHeader.py
│     └─ extractionCatSimple.py
|
├─ tests
|     ├─ ODD_VisualContagions.xml
|     ├─ ODD_VisualContagions.rng
|     ├─ testValidationxml.py
│     └─ test_entrees.py
|
├─ README.md
├─ requirements.txt
├─ resultat.xml
└─ run.py
```
