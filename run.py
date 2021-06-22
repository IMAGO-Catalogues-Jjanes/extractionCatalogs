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
import subprocess
from extractionCatSimple import extInfo_CatSimple
from creationTEIheader import creation_header



# récupération du chemin
dossier = input("Rentrer le dossier contenant les pages d'un même catalogue océsiré en alto XML 4: ")
nom_fichier_tei = input("Rentrer le nom du fichier TEI en output: ")
titre_fichier = input("Rentrer le nom du catalogue: ")


#création des balises tei, application du teiHeader et ajout, création des balises body-text-list
tei_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
tei_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titre_fichier
teiHeader = creation_header()
tei_xml.append(teiHeader)
text_xml = ET.SubElement(tei_xml, "text")
body_xml = ET.SubElement(text_xml, "body")
list_xml = ET.SubElement(body_xml, "list")

n_fichier = 0
for fichier in os.listdir(dossier):
    # parsage du fichier
    alto = ET.parse(dossier+fichier)
    # création TEI header
    # ici ajouter des tests pour vérifier la qualité de l'alto (cf le test.py)
    # lancement de l'extraction des données du fichier
    if n_fichier == 0:
        resultat_extraction = extInfo_CatSimple(alto, titre_fichier)
        n_division_list = 0
        for el in resultat_extraction:
            if n_division_list==0:
                list_entrees = el
            elif n_division_list==1:
                n_entree = el
            else:
                n_oeuvre = el
            n_division_list+=1
    else:
        resultat_extraction = extInfo_CatSimple(alto, titre_fichier, n_entree, n_oeuvre)
        n_division_list=0
        for el in resultat_extraction:
            if n_division_list==0:
                list_entrees = el
            elif n_division_list==1:
                n_entree = el
            else:
                n_oeuvre = el
            n_division_list+=1
    # ajout des nouvelles entrées dans la balise liste
    for el in list_entrees:
        list_xml.append(el)

# écriture du résultat dans un fichier xml
ET.ElementTree(tei_xml).write(nom_fichier_tei,encoding="UTF-8",xml_declaration=True)

# lancement des tests
bash_command= 'python -m unittest discover test'
process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
output, error = process.communicate()