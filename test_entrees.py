from shapely.geometry import Polygon
from lxml import etree as ET
import re

def verification_alto(document):
    """
    Fonction qui permet de vérifier, pour un document alto précis, si celui-ci est conforme à un schéma alto et contient
    toutes les informations nécessaires. Il rend en sortie une liste de 1 (l'élément est bien formé) et de 0 (l'élément
    est mal formé)
    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    :type document: ElementTree
    :return: List de valeurs. 1 lorsque le textLine se trouve bien dans le textBlock, 0 lorsque ce n'est pas le cas
    :rtype: list of str
    """
    try:
        fichier_xml = ET.parse(document)
    except etree.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme.
        print("Le fichier xml n'est pas bien formé. Corrigez le fichier"+ fichier_xml + " et relancez le programme.")
        sys.exit()


def calcul_pourcentage(list_resultat):
    """
    Fonction qui permet, pour une liste donnée, de calculer le pourcentage d'éléments ayant une valeur 1.
    :param list_resultat: Liste de 1 (bon) et 0 (mauvais)
    :type list_resultat: list
    :return: pourcentage de textLine et de textBlock bien formés
    :rtype: str
    """
    pourcentage = (sum(list_resultat)*100)/len(list_resultat)
    return pourcentage

def get_entries(document):
    """
    Fonction qui permet pour un document précis, de récupérer les coordonnées des textBlocks et des TextLines correspon-
    -dants et de les comparer pour vérifier si celles-ci sont bien dans les textBlocks entrées.
    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    :type document: ElementTree
    :return: pourcentage de fiabilité des entrées
    :rtype: int
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)
    list_resultat = []
    liste_entree = []
    for el in document.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree[0] + "']", namespaces=NS):
        # récupérer les coordonnées
        coord_V_block = float(el.xpath("@VPOS")[0])
        coord_H_block = float(el.xpath("@HPOS")[0])
        coord_width_block = float(el.xpath("@WIDTH")[0])
        coord_height_block = float(el.xpath("@HEIGHT")[0])
        # créer le polygone correspondant
        coord_block = [(coord_H_block, coord_V_block), (coord_H_block + coord_width_block, coord_V_block),
                       (coord_H_block + coord_width_block, coord_V_block + coord_height_block),
                       (coord_H_block, coord_V_block + coord_height_block)]
        poly_block = Polygon(coord_block)

        texte_entry = el.xpath("./alto:String/@CONTENT", namespaces=NS)
        for ligne in el.xpath(".//alto:TextLine", namespaces=NS):
            # récupérer les coordonnées de la ligne
            coord_V_line = float(ligne.xpath("@VPOS")[0])
            coord_H_line = float(ligne.xpath("@HPOS")[0])
            coord_width_line = float(ligne.xpath("@WIDTH")[0])
            coord_height_line = float(ligne.xpath("@HEIGHT")[0])
            # créer le polygone correspondant
            coord_line = [(coord_H_line, coord_V_line), (coord_H_line + coord_width_line, coord_V_line),
                          (coord_H_line + coord_width_line, coord_V_line + coord_height_line),
                          (coord_H_line, coord_V_line + coord_height_line)]
            poly_line = Polygon(coord_line)
            if poly_block.contains(poly_line):
                list_resultat.append(1)
            else:
                list_resultat.append(0)
    pourcentage_resultat = calcul_pourcentage(list_resultat)
    return pourcentage_resultat

