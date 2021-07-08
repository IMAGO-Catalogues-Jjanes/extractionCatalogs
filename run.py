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
from fonctions.extractionCatSimple import extInfo_CatSimple, extInfo_CatDouble
from fonctions.creationTEIheader import creation_header
from fonctions.restructuration import restructuration_automatique
from tests.testValidationxml import

# récupération du chemin
dossier = input("Rentrer le dossier contenant les pages d'un même catalogue océsiré en alto XML 4: ")
nom_fichier_tei = input("Rentrer le nom du fichier TEI en output: ")
titre_fichier = input("Rentrer le nom du catalogue: ")
# choix du type d'entrée à traiter
type_catalogue = input("""
1 pour un catalogue aux entrées de type simple
2 pour un catalogue aux entrées de type double
Rentrer le numéro correspondant aux entrées du catalogue:"""
                       )

#création des balises tei, application du teiHeader et ajout, création des balises body-text-list
tei_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
tei_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titre_fichier
teiHeader = creation_header()
tei_xml.append(teiHeader)
text_xml = ET.SubElement(tei_xml, "text")
body_xml = ET.SubElement(text_xml, "body")
list_xml = ET.SubElement(body_xml, "list")

n_fichier = 0
# pour chaque fichier alto (page du catalogue) on applique des opérations visant à vérifier la qualité de l'ocr produit
# et en fonction du résultat, on décide d'appliquer une récupération des éléments textuels via l'utilisation des entrées
# ou non
for fichier in sorted(os.listdir(dossier)):
    n_fichier +=1
    print("Traitement de "+fichier)
    # on vérifie que le fichier alto est bien formé
    verification_alto(dossier+fichier)
    # parsage du fichier
    alto = ET.parse(dossier+fichier)
    # on vérifie que la fiabilité de la formation des entrées
    pourcentage_fiabilite = get_entries(alto)
    #print(pourcentage_fiabilite)
    # on restructure l'alto afin d'avoir les textlines dans le bon ordre
    restructuration_automatique(dossier+fichier)
    #print("Restructuration du fichier faite")
    # parsage du fichier transformé
    document_alto = ET.parse(dossier+fichier[:-4]+"_restructuration.xml")


    # lancement de l'extraction des données du fichier
    if type_catalogue == "1":
        # les entrées sont simples, on lance directement la fonction correspondante
        if n_fichier == 1:
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_CatSimple(document_alto, titre_fichier, list_xml)
        else:
            # print("Numéro entrée: "+str(n_entree) + " Numéro oeuvre: "+ str(n_oeuvre))
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_CatSimple(alto, titre_fichier, list_xml, n_entree,
                                                                           n_oeuvre)
            # ajout des nouvelles entrées dans la balise liste
        for el in list_entrees:
            list_xml.append(el)
        print(fichier + "traité")
    elif type_catalogue == "2":
        """division_catalogue = input( => virgule point quadratin et la question des parenthèses
        Rentrer le numéro correspondant au type de division entre le nom d'un artiste et son information biographique
                                   )"""
        if n_fichier == 1:
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_CatDouble(document_alto, titre_fichier, list_xml)
        else:
            # print("Numéro entrée: "+str(n_entree) + " Numéro oeuvre: "+ str(n_oeuvre))
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_CatDouble(alto, titre_fichier, list_xml, n_entree,
                                                                           n_oeuvre)
            # ajout des nouvelles entrées dans la balise liste
        for el in list_entrees:
            list_xml.append(el)
        print(fichier + "traité")
    else:
        print("Le type de catalogue entré n'est pas compréhensible, veuillez relancer le programme.")

# écriture du résultat dans un fichier xml
ET.ElementTree(tei_xml).write(nom_fichier_tei,encoding="UTF-8",xml_declaration=True)

# lancement des tests
bash_command= 'python -m unittest discover test'
process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
output, error = process.communicate()

test_resultat(nom_fichier_tei)