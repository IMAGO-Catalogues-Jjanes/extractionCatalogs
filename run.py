"""
Initialisation du programme
Programme permettant, à partir de catalogues d'expositions océrisés avec Kraken, d'extraire les données contenues
dans le fichier de sortie de l'OCR (ALTO4 XML), et de construire un fichier TEI sur le modèle de l'ODD défini par
Caroline Corbières (https://github.com/carolinecorbieres/ArtlasCatalogues/blob/master/5_ImproveGROBIDoutput/ODD/ODD_Transformation.xml)

Le programme est particulièrement adapté à un traitement à partir d'eScriptorium, une interface pour kraken permettant de visualiser
le processus de segmentation puis d'obtenir les fichier ALTO4 nécessaires à cette pipeline.

Author: Juliette Janes
Date: 11/06/21
Continué par Esteban Sánchez Oeconomo 2022
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


# E: commandes obligatoires :
@click.command()
@click.argument("directory", type=str)
@click.argument("output", type=str, required=True)
@click.argument("typecat", type=click.Choice(['Nulle', "Simple", "Double", "Triple"]), required=True)
# E : options
@click.option("-n", "--name", "titlecat", type=str,
              help="Select a custom name for the catalog id in the TEI output. By default, it takes the output name")
@click.option("-st", "--segtrans", "segmentationtranscription", is_flag=True, default=False,
              help="automatic segmentation and transcription via kraken. Input files must be images.")
@click.option("-v", "--verify", "verifyalto", is_flag=True, default=False,
              help="verify ALTO4 input files conformity and structure")
def extraction(directory, titlecat, typecat, output, segmentationtranscription, verifyalto):
    """
    Python script taking a directory containing images or alto4 files of exhibition catalogs in input and giving back an
    XML-TEI encoded catalog

    directory: path to the directory containing images or alto4 files
    output: name of the TEI file output
    typeCat: catalog's type according to the division done in the github of the project (Nulle, Simple, Double or Triple)
    titlecat: name of the processed catalog. It takes the output name by default but can be customized with -n command
    -st: take image files as an input instead of ALTO4. Automatic segmentation and transcription occurs via kraken.
    -v: verify ALTO4 files.
    """

    # E : si aucun nom n'a été donné au catalogue avec la commande -n, il prend pour nom la valeur de l'output choisi :
    if not titlecat:
        titlecat = output
        # E : si le nom de l'output contient une extension ".xml", on l'enlève
        if titlecat.__contains__(".xml"):
            titlecat = titlecat[:-3]
        else:
            pass
    else:
        pass

    # E : si l'on souhaite segmenter et océrriser automatiquement (-st) :
    # TODO : les commandes kraken ne semblent plus d'actualité ; vérifier fonction
    if segmentationtranscription:
        print("Segmentation et transcription automatiques en cours")
        # E : on appelle le module transcription (fichier kraken_automatic.py) :
        transcription(directory)
        # E : on réactualise le chemin de traitement vers le dossier contenant les nouveaux ALTO4 :
        directory="./temp_alto/"
    else:
        pass

    # E : création des balises TEI (teiHeader, body) avec le paquet lxml et le module creationTEI.py :
    root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titlecat
    # E : on crée le teiHeader avec la fonction correspondante (module creationTEI.py) :
    teiHeader_xml = creation_header()
    # E : on l'ajoute à l'arborescence :
    root_xml.append(teiHeader_xml)
    # E : on créé les balises imbriquées text, body et list :
    text_xml = ET.SubElement(root_xml, "text")
    body_xml = ET.SubElement(text_xml, "body")
    list_xml = ET.SubElement(body_xml, "list")
    # E : on créé une liste vide avec laquelle on comptera les fichiers traités :
    n_fichier = 0

    # E : pour chaque fichier ALTO (page transcrite du catalogue), on contrôle sa qualité si la commande -v est
    # activée, puis l'on récupère les éléments textuels des entrées :
    for fichier in sorted(os.listdir(directory)):
        # E : exclusion des dossiers/fichiers cachés (".[...]"). Cela rend le script fonctionnel sur mac (.DS_Store)
        # E : exclusion des fichiers "restructuration" pour pouvoir relancer le script en évitant des boucles.
        # E : exclusion de fichiers autres que XML (permet la présence d'autres types de fichiers dans le dossier)
        if not fichier.startswith(".") and not fichier.__contains__("restructuration") and fichier.__contains__(".xml"):
            # E : on ajoute le ficher au comptage et on l'indique sur le terminal :
            n_fichier += 1
            print(str(n_fichier) + " – Traitement de " + fichier)
            if verifyalto:
                # E : si la commande verify (-v) est activée, on appelle les fonctions du module test_Validations_xml.py
                # pour vérifier que le fichier ALTO est bien formé et que la structure des entrées est respectée :
                print("\tVérification de la formation du fichier alto: ")
                check_strings(directory+fichier)
                print("\tVérification de la structure des entrées: ")
                get_entries(directory+fichier)
            else:
                pass
            # E : on appelle le module restructuration.py pour restructurer l'ALTO et avoir les textlines dans le bon ordre :
            restructuration_automatique(directory + fichier)
            print('\tRestructuration du fichier effectuée (fichier "_restructuration.xml" créé)')
            # E : on indique le chemin vers le fichier restructuré et on le parse :
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
            print("\t" + fichier + " traité")

    # E : on créé une variable contenant l'arbre
    xml_tree = ET.ElementTree(root_xml)
    # E : on créé des variables avec les schémas souhaités
    # (en ligne et pas en local pour faciliter la mobilité des documents) :
    schema_1 = ET.ProcessingInstruction('xml-model', 'href="https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/extractionCatalogs/main/tests/out/ODD_VisualContagions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"')
    schema_2 = ET.ProcessingInstruction('xml-model', 'href="https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/extractionCatalogs/main/tests/out/ODD_VisualContagions.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"')
    # Feuille de style pour présenter les catalogues sur un navigateur :
    # TODO à refaire en totalité
    # ne marche que en local, voici le lien souhaité : https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/TEIcatalogs/main/affichage_TEI.css
    CSS = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="affichage_TEI.css"')
    # E : on peut rajouter ces instructions au dessus de la racine – ils sont traités comme des noeuds :
    xml_tree.getroot().addprevious(schema_1)
    xml_tree.getroot().addprevious(schema_2)
    xml_tree.getroot().addprevious(CSS)

    # E : écriture du résultat de tout le processus de création TEI dans un fichier xml
    xml_tree.write(output, encoding="UTF-8", xml_declaration=True)


if __name__ == "__main__":
    extraction()
