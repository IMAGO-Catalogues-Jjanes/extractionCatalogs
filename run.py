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
from PIL import Image
from fonctions.extractionCatEntrees import extInfo_Cat
from fonctions.creationTEIheader import creation_header
from fonctions.restructuration import restructuration_automatique
from fonctions.test_Validations_xml import verification_alto, get_entries, association_xml_rng

# récupération du chemin
dossier = input("Rentrer le dossier contenant les pages d'un même catalogue océsiré en alto XML 4: ")
output_tei = input("Rentrer le nom du fichier TEI en output: ")
titre_catalogue = input("Rentrer le nom du catalogue: ")
# choix du type d'entrée à traiter
while True:
    type_catalogue = input("""
            Nulle pour un catalogue aux entrées de type nulle
            Simple pour un catalogue aux entrées de type simple
            Double pour un catalogue aux entrées de type double
            Triple pour un catalogue aux entrées de type Triple
            Rentrer le type correspondant aux entrées du catalogue en vous référant aux exemples présentés dans le github:"""
                           )
    if type_catalogue not in ('Nulle', 'Simple', 'Double', 'Triple'):
        print('Mauvais type de catalogue.')
    else:
        break

#création des balises tei, application du teiHeader et ajout, création des balises body-text-list
root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titre_catalogue
teiHeader_xml = creation_header()
root_xml.append(teiHeader_xml)
text_xml = ET.SubElement(root_xml, "text")
body_xml = ET.SubElement(text_xml, "body")
list_xml = ET.SubElement(body_xml, "list")

n_fichier = 0
# pour chaque fichier alto (page du catalogue) on applique des opérations visant à vérifier la qualité de l'ocr produit
# et en fonction du résultat, on décide d'appliquer une récupération des éléments textuels via l'utilisation des entrées
# ou non
for fichier in sorted(os.listdir(dossier)):
    n_fichier +=1
    print("Traitement de "+fichier)
    # on vérifie que le fichier alto est valide
    verification_alto(dossier+fichier)
    # on vérifie que les entrées sont bien formées
    #get_entries(dossier+fichier)
    # on restructure l'alto afin d'avoir les textlines dans le bon ordre
    restructuration_automatique(dossier+fichier)
    print("Restructuration du fichier faite")
    # parsage du fichier transformé
    document_alto = ET.parse(dossier+fichier[:-4]+"_restructuration.xml")
    # lancement de l'extraction des données du fichier
    # les entrées sont simples, on lance directement la fonction correspondante
    if n_fichier == 1:
        list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, type_catalogue, titre_catalogue,
                                                                 list_xml)
    else:
        # print("Numéro entrée: "+str(n_entree) + " Numéro oeuvre: "+ str(n_oeuvre))
        list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, type_catalogue, titre_catalogue,
                                                                       list_xml, n_entree,n_oeuvre)
    # ajout des nouvelles entrées dans la balise liste
    for el in list_entrees:
        list_xml.append(el)
    print(fichier + "traité")
# écriture du résultat dans un fichier xml
ET.ElementTree(root_xml).write(output_tei,encoding="UTF-8",xml_declaration=True)

# lancement des tests (fichier tei valide et comparaison avec un fichier qui n'a pas utilisé l'alto)
association_xml_rng(output_tei)