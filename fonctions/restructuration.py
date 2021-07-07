#import des librairies nécessaires
import os
import click
import re
from lxml import etree as ET
import errno

def restructuration_automatique(fichier):
    """
    Fonction permettant, pour chaque fichier d'un dossier donné, de lui appliquer la feuille de transformation
    transformation_alto.xsl qui permet de restructurer dans le bon ordre l'output alto de Kraken.
    :param fichier: chaîne de caractères correspondant au chemin relatif du fichier à transformer
    :type fichier: str
    :return: fichier AlTO contenant une version corrigée de l'input
    :return: file
    """

    # on applique la feuille de transformation de correction
    original = ET.parse(fichier)
    transformation_xlst = ET.XSLT(ET.parse("./fonctions/Restructuration_alto.xsl"))
    propre = transformation_xlst(original)
    # on créé un nouveau fichier dans le dossier résultat
    with open(fichier[:-4] + "_restructuration.xml", mode='wb') as f:
        f.write(propre)
