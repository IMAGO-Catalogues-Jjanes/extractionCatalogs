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
import click
from fonctions.extractionCatEntrees import extInfo_Cat
from fonctions.creationTEI import creation_header
from fonctions.restructuration import restructuration_automatique
from tests.test_Validations_xml import check_strings, get_entries, association_xml_rng
from fonctions.automatisation_kraken.kraken_automatic import transcription


@click.command()
@click.argument("directory", type=str)
@click.argument("titlecat", type=str)
@click.argument("typecat", type=click.Choice(['Nulle', "Simple", "Double", "Triple"]), required=True)
@click.argument("output", type=str, required=True)
@click.option("-st", "--segtrans", "segmentationtranscription", is_flag=True, default=False)
@click.option("-v", "--verify", "verifyalto", is_flag=True, default=False)
def extraction(directory, titlecat, typecat, output, segmentationtranscription, verifyalto):
    """
    Python script taking a directory containing images or alto4 files of exhibition catalogs in input and giving back an
    XML-TEI encoded catalog

    directory: path to the directory containing images or alto4 files
    titlecat: name of the processed catalog (in the form title_date)
    typeCat: catalog's type according to the division done in the github of the project (Nulle, Simple, Double or Triple)
    output: name of the TEI file output
    -st: if you have a group of images in input, in order to transcribe them in the program. Otherwise, you need Alto4 files
    in input.
    -v: if you want to verify your alto4 files.
    """
    if segmentationtranscription:
        # si l'option segmentation et transcription automatique est activée, on transcrit les images et on réattribue
        # à la variable directory une nouvelle valeur vers le dossier contenant les altos.
        print("Transcription en cours")
        transcription(directory)
        directory="./temp_alto/"
    else:
        pass

    # création des balises du fichier TEI (Teiheader et body)
    root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titlecat
    teiHeader_xml = creation_header()
    root_xml.append(teiHeader_xml)
    text_xml = ET.SubElement(root_xml, "text")
    body_xml = ET.SubElement(text_xml, "body")
    list_xml = ET.SubElement(body_xml, "list")
    n_fichier = 0
    # pour chaque fichier alto (page du catalogue) on applique des opérations visant à vérifier la qualité de l'ocr produit
    # et en fonction du résultat, on décide d'appliquer une récupération des éléments textuels via l'utilisation des entrées
    # ou non
    for fichier in sorted(os.listdir(directory)):
        n_fichier += 1
        print("Traitement de " + fichier)
        if verifyalto:
            # si l'option verify est activée, on lance sur le fichier alto les fonctions vérifiant que le fichier est bien
        # formé et que la structure des entrées est respectée
            print("Vérification de la formation du fichier alto: ")
            check_strings(directory+fichier)
            print("Vérification de la structure des entrées: ")
            get_entries(directory+fichier)
        else:
            pass
        # on restructure l'alto afin d'avoir les textlines dans le bon ordre
        restructuration_automatique(directory + fichier)
        print("Restructuration du fichier faite")
        # parsage du fichier transformé
        document_alto = ET.parse(directory + fichier[:-4] + "_restructuration.xml")
        # lancement de l'extraction des données du fichier
        # les entrées sont simples, on lance directement la fonction correspondante
        if n_fichier == 1:
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat,
                                                                     list_xml)
        else:
            list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat,
                                                                     list_xml, n_entree, n_oeuvre)
        # ajout des nouvelles entrées dans la balise liste
        for el in list_entrees:
            list_xml.append(el)
        print(fichier + "traité")
    # écriture du résultat dans un fichier xml
    ET.ElementTree(root_xml).write(output, encoding="UTF-8", xml_declaration=True)

    # lancement des tests (fichier tei valide et comparaison avec un fichier qui n'a pas utilisé l'alto)
    association_xml_rng(output)

if __name__ == "__main__":
    extraction()