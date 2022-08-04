import os
import click
import re
from lxml import etree as ET
import errno

def XML_to_CSV(output_file, extraction_directory, titlecat):
    """
    Créé un fichier CSV adapté au projet Artl@s à partir d'un catalogue encodé en TEI
    La feuille de transformation XMLtoCSV a été fournie par Ljudmila PetKovic

    :param output_file: chemin vers le fichier TEI à convertir en CSV
    """
    try:
        tei = ET.parse(output_file)
        feuille = ET.parse("./extractionCatalogs/fonctions/XMLtoCSV.xsl")
        feuille_simple = ET.parse("./extractionCatalogs/fonctions/XMLtoCSVsimple.xsl")

        transformation_xslt = ET.XSLT(feuille)
        transformation_xslt_simple = ET.XSLT(feuille_simple)

        csv = transformation_xslt(tei)
        csv_simple = transformation_xslt_simple(tei)

        chemin_csv = extraction_directory + "/CSV/" + titlecat + "_tableau.csv"
        chemin_csv_simple = extraction_directory + "/CSV/" + titlecat + "_tableau_simple.csv"

        os.makedirs(os.path.dirname(chemin_csv), exist_ok=True)
        os.makedirs(os.path.dirname(chemin_csv_simple), exist_ok=True)

        with open(chemin_csv, mode='wb') as f:
            f.write(csv)
        with open(chemin_csv_simple, mode='wb') as f:
            f.write(csv_simple)
        csv_produit = True

    except:
        csv_produit = False

    return csv_produit

def csv_immediat(titlecat, output_file, extraction_directory):
    # on redonne au catalogue sa terminaison en ".xml" afin de construire le chemin vers le fichier TEI
    output_file = output_file + ".xml"
    # on appelle la fonction qui produit un fichier csv :
    csv_produit = XML_to_CSV(output_file, extraction_directory, titlecat)
    # on construit le chemin qui doit mener vers ce fichier csv :
    chemin_csv = extraction_directory + "/CSV/" + titlecat + "_tableau.csv"

    print("\n    Création d'un tableur csv :")

    # si le fichier n'a pas été produit, on signale l'erreur :
    if not os.path.exists(output_file):
        print("\t[!] aucun fichier csv n'a été produit.")
        #  si le dossier indiqué est vide, c'est qu'il a mal été écrit et il faut le supprimer :
        if not os.listdir(extraction_directory):
            os.removedirs(extraction_directory)
            print("\t    Le chemin output et/ou le nom de catalogue indiqués ne mènent vers aucun fichier TEI à transformer.\n")

    else:
        # si le fichier TEI existe, mais qu'il n'y a pas de csv produit, c'est au niveau de la création csv qu'il y a eu un problème :
        if csv_produit == False:
            print("\t[!] Le fichier csv n'a pas été produit. Vérifiez la conformité du fichier TEI.\n")

    if csv_produit == True:
        print("\t ✓ Le fichier csv a été produit"
              "\n\t   Chemin du fichier : {} \n".format(chemin_csv))







