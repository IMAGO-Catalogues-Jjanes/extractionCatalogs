"""
Script de test permettant de vérifier l'adéquation du fichier XML_TEI au schéma RNG du projet
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

from lxml import etree as ET
import sys
import re
from urllib.request import urlopen
from ...variables.contenu_TEI import lien_schema


def association_xml_rng(document_xml):
    """
    Fonction qui vérifie la conformité du XML-TEI produit au schéma rng du projet en cours. Ce schéma doit être indiqué
    dans le dossier variables, dans le gabarit du projet en cours.
    :param schema_rng: schéma RelaxNG comprenant la structure définie dans l'ODD du projet
    :type schema_rng: str
    :param document_xml: fichier xml tei de travail parsé par etree
    :type document_xml: str
    :return resultat: chaîne de caractères validant le fichier xml tei
    :type resultat:str
    """
    # on parse le document xml pour le récupérer
    try:
        fichier_xml = ET.parse(document_xml)
    # on vérifie dans un premier temps s'il est conforme xml :
    except ET.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme :
        print("\tLe fichier xml n'est pas bien formé.")
        sys.exit()

    # récupération et parsage du fichier rng du projet :
    # pour utiliser le document en local :
    # relaxng_fichier = ET.parse("extractionCatalogs/fonctions/validation_alto/out/ODD_VisualContagions.rng")
    url = urlopen(lien_schema)
    relaxng_fichier = ET.parse(url)
    # Si l'on préfère utiliser le document en local :
    # relaxng_fichier = ET.parse("extractionCatalogs/fonctions/validation_alto/out/ODD_VisualContagions.rng")
    relaxng = ET.RelaxNG(relaxng_fichier)
    # association du relaxng et du fichier tei
    if relaxng(fichier_xml):
        # s'il est conforme, la terminal l'indique. Cela n'arrivera que dans les cas où les ALTO en input ont été
        # parfaitement encodés et corrigés préalablement
        resultat= "tei valide"
        print("\tLe document XML produit est conforme au schéma TEI et à l'ODD du projet.")
    else:
        # on signale que le document n'est pas valide. Ce sera le cas dans la très grande majorité des cas,
        # et il est normal de devoir faire des corrections manuelles pour compléter l'extraction automatique
        print("\tLe document XML produit n'est pas conforme au schéma TEI et à l'ODD du projet ; il nécessite des corrections manuelles ")
        resultat= "tei non valide"
    return resultat

def get_entries(chemin_document):
    """
    Fonction qui permet pour un document précis, de vérifier que l'alto est construit de façon à ce que les TextBlocks
    entrées contiennent les TextLines correspondantes et que celles-ci ne sont pas contenues dans le TextBlock main.
    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    document = ET.parse(chemin_document)
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
    tagrefs_list = document.xpath("//alto:OtherTag/@ID", namespaces=NS)
    textline_list = document.xpath("//alto:TextLine", namespaces=NS)
    for textline in textline_list:
        parent_textblock = textline.getparent()
        n_zone_non_entree = 0
        try:
            tagrefs_textblock = parent_textblock.attrib['TAGREFS']
            if tagrefs_textblock != tagref_entree:
                if tagrefs_textblock in tagrefs_list:
                    n_zone_non_entree +=1
                else:
                    print("\tL'entrée " + str(parent_textblock.attrib['ID']) + " n'est pas bien formée.")
                    action = input("Voulez-vous annuler le programme (1) ou passer outre (2) ? (Attention : des résultats peuvent être mis de coté)")
                    if action == "1":
                        sys.exit()
                    elif action == "2":
                        pass
        except Exception:
            print("\tL'entrée " + str(parent_textblock.attrib['ID']) + " n'est pas bien formée.")
            action = input("Voulez-vous annuler le programme (1) ou passer outre (2) ? (Attention : des résultats peuvent être mis de coté)")
            if action == "1":
                sys.exit()
            elif action == "2":
                pass
    if n_zone_non_entree > 3:
        print("\tIl y a plus de 3 zones qui ne sont pas des zones entrées.")
        action = input("Voulez-vous annuler le programme (1) ou passer outre (2) ? (Attention : des résultats peuvent être mis de coté)")
        if action == "1":
            sys.exit()
        elif action == "2":
            pass

def check_strings(fichier):
    """
    Fonction qui permet, pour un alto donné, de vérifier sa bonne formation et de la corriger si elle est mauvaise.
    Légèrement adapté d'un script produit par Claire Jahan.
    :param fichier: chemin du fichier à vérifier
    :return problemes:
    :type problemes: list
    """

    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    file = ET.parse(fichier)
    root = file.getroot()
    # on selectionne le troisième ensemble de balises du fichier, appelé "layout", et on va boucler sur chaque niveau
    layout = root[2]
    # on récupère l'identifiant des DefaultLine, qui correspondent aux balises TextLine
    tagref_default = file.xpath("//alto:OtherTag[@LABEL='DefaultLine']/@ID", namespaces=NS)[0]
    # TODO pourquoi la méthode append() ne marche pas ici dans les itérations qui suivent pour la liste problemes ?
    # TODO c'est les objets etree qui posent problème pour cela ? les variables probleme* sont imprimées comme attendu
    # TODO mais l'appen semble n'avoir lieu qu'après la fin de l'ensemble des itérations et non pas une après l'autre, donc la liste reste vide
    problemes = []
    problemes_dic = {}
    # pour chaque balise page
    for page in layout:
        # pour chaque balise printspace contenue dans les page
        for printspace in page:
            # pour chaque balise textblock contenue dans les printspace
            for textblock in printspace:
                # on vérifie si des textblock sont mal ou pas référencées
                # (le script les mets de côté, il est donc important de vérifier s'ils contiennent des informations à extraire)
                if textblock.get("ID") == "eSc_dummyblock_":
                    probleme1 = "\tLe fichier contient une balise TextBlock '" + textblock.get("ID") + \
                                " ; celle ci n'est pas conforme à l'ontologie du projet. " + \
                                "\n\tSi elle contient des informations à extraire, il faut la supprimer et mettre le contenu dans un TextBlock conforme."
                    problemes.appeend(probleme1)
                    problemes_dic[textblock.get("ID")] = probleme1
                    print(problemes_dic)
                    print(probleme1)
                elif textblock.get("TAGREFS") == None:
                    probleme2 = "\tLe fichier contient une balise TextBlock '" + textblock.get("ID") + \
                                "' sans TAGREF, donc non associé à l'ontologie du projet."
                    problemes.append(probleme2)
                    print(probleme2)
                elif textblock.get("TAGREFS") == "BT":
                    probleme3 = "\tLe fichier contient une balise TextBlock '" + textblock.get("ID") + \
                                "' dont l'attribut TAGREF est incomplet. " + \
                                "\n\tS'il contient des informations à extraire, il faut le compléter pour l'associer à l'ontologie du projet."
                    problemes.append(probleme3)
                    print(probleme3)
    print(problemes_dic)
    for page in layout:
        # pour chaque balise printspace contenue dans les page
        for printspace in page:
            # pour chaque balise textblock contenue dans les printspace
            for textblock in printspace:
                # pour chaque balise textline contenue dans les textblock
                for textline in textblock:
                    if textline.tag == "{http://www.loc.gov/standards/alto/ns-v4#}TextLine":
                        # si la balise contient un attribut TAGREFS conforme, tout va bien
                        if textline.get("TAGREFS") == tagref_default:
                            pass
                        # autrement, on le signale dans le terminal
                        else:
                            probleme4 = "\tle fichier contient une balise TextLine '" + textline.get("ID") + \
                                        "' sans TAGREF correspondant à l'ontologie du projet."
                            problemes.append(probleme4)
                            print(probleme4)
    # TODO la liste retournée est vide !
    return problemes
