"""
Initialisation du programme
Programme permettant, à partir de catalogues d'expositions océrisés avec Kraken, d'extraire les données contenues
dans le fichier de sortie de l'OCR, ALTO XML, et de construire un fichier TEI sur le modèle de l'ODD défini par
Caroline Corbières (https://github.com/carolinecorbieres/ArtlasCatalogues/blob/master/5_ImproveGROBIDoutput/ODD/ODD_Transformation.xml)

Author: Juliette Janes
Date: 11/06/21
"""
from lxml import etree as ET
import os
from extractionCatSimple import extInfo_CatSimple



# récupération du chemin
dossier = input("Rentrer le dossier contenant les pages d'un même catalogue océsiré en alto XML 4: ")
nom_fichier_tei = input("Rentrer le nom du fichier TEI en output: ")
#création de la balise list contenant toutes les entrées du catalogue
root_list_xml = ET.Element("list")

for fichier in os.listdir(dossier):
    # parsage du fichier
    alto = ET.parse(dossier+fichier)
    # création TEI header
    # ici ajouter des tests pour vérifier la qualité de l'alto (cf le test.py)
    # lancement de l'extraction des données du fichier
    list_entrees = extInfo_CatSimple(alto)
    # ajout des nouvelles entrées dans la balise liste
    for el in list_entrees:
        root_list_xml.append(el)

# écriture du résultat dans un fichier xml
ET.ElementTree(root_list_xml).write(nom_fichier_tei,encoding="UTF-8",xml_declaration=True)

