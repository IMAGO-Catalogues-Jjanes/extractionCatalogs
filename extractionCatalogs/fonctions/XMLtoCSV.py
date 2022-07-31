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
    tei = ET.parse(output_file)
    feuille = ET.parse("./extractionCatalogs/fonctions/XMLtoCSV.xsl")
    transformation_xslt = ET.XSLT(feuille)
    csv = transformation_xslt(tei)

    chemin_csv = extraction_directory + "/CSV/" + titlecat + "_tableau.csv"

    os.makedirs(os.path.dirname(chemin_csv), exist_ok=True)
    with open(chemin_csv, mode='wb') as f:
        f.write(csv)
    return chemin_csv