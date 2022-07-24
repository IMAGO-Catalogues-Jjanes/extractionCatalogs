# extractionCatalogs : Python data extractor for exhibition catalogs

This python script aims to create TEI encoded exhibition catalogs from XIXth and XXth centuries.

It uses Alto4 files as an input (which contains the catalogs segmentation and transcriptions) and delivers XML-TEI files. 
You can find in [here](https://github.com/Juliettejns/TEIcatalogs) examples of data produced with this script.

## Using the pipeline
<div align="justify">
   
   <p class="float" align="center">
      <img src="extractionCatalogs/static/images/pipeline_extraction.png"/>
   </p>
   
   Since the transcription of the exhibition catalogs pages are done along to its layout analysis, entries are described in the alto4 file. Therefore, we are able, for each entry, to get, using regular expressions, the author, its biographic informations and each items created by the author. To do that, we need to divide exhibition catalogs according to their entries' typology: 

   
   1. Null: An entry is composed of the name of the author and the different items.<br/>
   2. Simple: Each line of the entry contains an precise element: author, biographic informations, item's title and other informations.<br/>
   3. Double: The author and his biographic informations are on the same line. Item's title and its other informations are on two separated lines.<br/>

   <p class="float" align="center">
      <img src="extractionCatalogs/static/images/entree_nulle.png" height="150"/>
      <img src="extractionCatalogs/static/images/Exemple_Entree_Simple.png" height="150"/>
      <img src="extractionCatalogs/static/images/Exemple_Entree_Double.png" height="150" width="400"/>
   </p>
Left to right: Null entry, Simple entry and Double entry
   <br/>
   
The regular expressions are instancied in the ```regex_instanciation.py``` file. Various regular expressions have been created in order to match with most of the exhibition catalogs. Therefore, it is needed, before using the python script, to check this file and verify that the activated regular expressions match the processed catalog.
   
The script output is a XML-TEI file which combines all the Alto4 transcriptions and sticks to the [ODD](https://github.com/carolinecorbieres/ArtlasCatalogues/blob/master/5_ImproveGROBIDoutput/ODD/ODD_VisualContagions.xml) done by Caroline Corbières. The ```Teiheader``` is not completed. 
   

</div>
 
## Installation
  - Clone the repository: ```git clone https://github.com/Juliettejns/extractionCatalogs```
  - Create virtual environment: ```virtualenv -p python3 env```
  - Run the virtual env: ```source env/bin/activate```
  - Install the requirements: ```pip install -r requirements.txt```
  - Check the regex used in the `fonctions/instanciation_regex.py` file
  - Run the program (previously): `python3 run.py input_dir output_dir catalogue_title -st`

If you want to have images as your input, you need to add the option `-st` at the end of the command. It segments and transcribes your data.</br>
  - Stop the virtual env: ```source env/bin/deactivate```

## Repository

```
├── fonctions
│     ├── automatisation_kraken
│     │     ├─ automatic_kraken.py
|     |     ├─ model_ocr.mlmodel
│     │     └─ model_segmentation.mlmodel
│     │ 
│     ├── creationTEI.py
│     ├── restructuration_alto.xsl
│     ├── restructuration.py
│     ├── creationEntreeCat.py
│     └─ instanciation_regex.py
|
├── tests
│     ├── out
│     │     └─ ODD_VisualContagions.rng
│     ├── ODD_VisualContagions.xml
│     └─ test_Validation_xml.py
|
├── images
├── README.md
├── requirements.txt
└─ run.py
```

## Credits
This repository was first developed by Juliette Janes in 2021. The project was further augmented by Esteban Sánchez Oeconomo in 2022.

Both former students in Digital Humanities at Paris Science-Lettres University and interns of the [Artl@s](https://artlas.huma-num.fr/fr/) 
project worked under the direction of Simon Gabay and Béatrice Joyeux-Prunel.

## Thanks to
This project greatly benefited from the active help of Simon Gabay, Claire Jahan and Frédérine Pradier

## Licence
The code is CC-BY.</br>
![68747470733a2f2f692e6372656174697665636f6d6d6f6e732e6f72672f6c2f62792f322e302f38387833312e706e67](https://user-images.githubusercontent.com/56683417/115525743-a78d2400-a28f-11eb-8e45-4b6e3265a527.png)

## Cite this repository
Juliette Janes, Simon Gabay, Béatrice Joyeux-Prunel, _extractionCatalogs: Python data extractor for exhibition catalogs_, 2021, Paris: ENS Paris https://github.com/Juliettejns/TEIcatalogs/

Esteban Sánchez Oeconomo, Juliette Janès, Simon Gabay, Béatrice Joyeux-Prunel, _extractionCatalogs: Python data extractor for exhibition catalogs_, 2022, Paris: ENS Paris, IMAGO / Genova: Université de Genève


## Contacts
If you have any questions or remarks, please contact juliette.janes@chartes.psl.eu, esteban.sanchez.oeconomo@chartes.psl.eu or simon.gabay@unige.ch.

