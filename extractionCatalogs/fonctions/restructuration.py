import os
import click
import re
from lxml import etree as ET
import errno

def restructuration_automatique(directory, fichier, extraction_directory):
    """
    Fonction permettant, pour chaque fichier d'un dossier donné, de lui appliquer la feuille de transformation
    transformation_alto.xsl qui permet de restructurer dans le bon ordre les élémements de l'output alto de Kraken.
    Ces éléments peuvent être en effet en désordre en fonction de l'ordre dans lequel ils ont été saisis.
    Cette ordre est déterminé en fonction de la règle XSLT <xsl:sort select="./a:String/@VPOS" data-type="number"/>

    :param fichier: chaîne de caractères correspondant au chemin relatif du fichier à transformer
    :type fichier: str
    :return: fichier AlTO contenant une version corrigée de l'input, dans un nouveau dossier "restructuration", ainsi
    qu'une variable chemin_restructuration qui contient son chemin
    :return: file
    """

    # on applique la feuille de transformation de correction
    original = ET.parse(directory + fichier)
    transformation_xlst = ET.XSLT(ET.parse("./extractionCatalogs/fonctions/Restructuration_alto.xsl"))
    propre = transformation_xlst(original)
    # on créé un nouveau fichier dans le dossier résultat
    chemin_restructuration = extraction_directory + "/restructuration ALTO/" + fichier[:-4] + "_restructuration.xml"
    os.makedirs(os.path.dirname(chemin_restructuration), exist_ok=True)
    with open(chemin_restructuration, mode='wb') as f:
        f.write(propre)
    return chemin_restructuration

