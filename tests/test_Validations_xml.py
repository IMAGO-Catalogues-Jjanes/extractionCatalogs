"""
Script de test permettant de vérifier l'adéquation du fichier XML_TEI au schéma RNG du projet
Author:Juliette Janes
Date: 26/03/2021
"""

from lxml import etree as ET
import sys
import re

def association_xml_rng(document_xml):
    """
    Fonction qui ajoute le schéma rng au document xml tei afin de vérifier leur adéquation.
    :param schema_rng: schéma RelaxNG comprenant la structure définie dans l'ODD du projet (NDF_ODD.xml)
    :type schema_rng: str
    :param document_xml: fichier xml tei de travail parsé par etree
    :type document_xml: str
    :return resultat: chaîne de caractères validant le fichier xml tei
    :type resultat:str
    """
    # on parse le document xml pour le récupérer
    try:
        fichier_xml = ET.parse(document_xml)
    except ET.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme.
        print("Le fichier xml n'est pas bien formé.")
        sys.exit()

    # récupération et parsage en tant que relaxng du fichier rng
    relaxng_fichier = ET.parse('./tests/ODD_VisualContagions.rng')
    relaxng = ET.RelaxNG(relaxng_fichier)

    # association du relaxng et du fichier tei
    if relaxng(fichier_xml):
        # si le document est valide on stocke dans la variable resultat une chaîne de caractère validant le document
        resultat= "tei valide"
        print("Le document XML est conforme au schéma TEI et à l'ODD du projet.")
    else:
        # sinon on signale que le document n'est pas valide et on ajoute les messages d'erreurs
        print("Le document XML n'est pas conforme au schéma TEI et à l'ODD du projet." + relaxng.assertValid(fichier_xml))

    return resultat

def get_entries(chemin_document):
    """
    Fonction qui permet pour un document précis, de vérifier que l'alto est construit de façon à ce que les TextBlocks
    entrées contiennent les TextLines correspondantes et que celles-ci ne sont pas contenues dans le TextBlock main.
    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    document = ET.parse(chemin_document)
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)[0]
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
                    print("L'entrée " + str(parent_textblock.attrib['ID']) + " n'est pas bien formée.")
                    action = input("""Voulez-vous revoir votre alto (1) ou
                                            passer outre (2). Attention le résultat risque d'oublier des entrées.""")
                    if action == "1":
                        sys.exit()
                    elif action == "2":
                        pass
        except Exception:
            print("L'entrée " + str(parent_textblock.attrib['ID']) + " n'est pas bien formée.")
            action = input("""Voulez-vous revoir votre alto (1) ou
                                    passer outre (2). Attention le résultat risque d'oublier des entrées.""")
            if action == "1":
                sys.exit()
            elif action == "2":
                pass
    if n_zone_non_entree > 3:
        print("Il y a plus de 3 zones qui ne sont pas des zones entrées.")
        action = input("""Voulez-vous vérifier la structure de votre page(1) ou
                                                    passer outre (2). Attention le résultat risque d'oublier des entrées.""")
        if action == "1":
            sys.exit()
        elif action == "2":
            pass

def check_strings(fichier):
    """
    Fonction qui permet, pour un alto donné, de vérifier sa bonne formation et de la corriger si elle est mauvaise.
    Légèrement adapté d'un script produit par Claire Jahan.
    :param fichier: chemin du fichier à vérifier
    :return:
    """

    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    file = ET.parse(fichier)
    root = file.getroot()
    strings = ET.tostring(root, encoding='unicode')
    strings = strings.split("\n")
    layout = root[2]
    final = ""
    tagref_default = file.xpath("//alto:OtherTag[@LABEL='Default']/@ID", namespaces=NS)[0]
    for page in layout:
        for printspace in page:
            for textblock in printspace:
                if textblock.get("TAGREFS") == None:
                    print("Le block " + textblock.get("ID") + " du fichier " + fichier + " n'a pas de "
                                                                                           "type. Ce block"
                                                                                           " est à complét"
                                                                                           "er (ajouter "
                                                                                           "un TAGREFS) "
                                                                                           "ou à supprimer.")
                elif textblock.get("TAGREFS") == "BT":
                    print("Le block " + textblock.get("ID") + " du fichier " + fichier + " a un attribut "
                                                                                           "TAGREFS incomplet. "
                                                                                           "Il faut le compléter.")
                elif textblock.get("ID") == "eSc_dummyblock_":
                    print("Le block " + textblock.get("ID") + " du fichier " + fichier + " n'est pas un block "
                                                                                           "correct. Il faut le "
                                                                                           "supprimer et ajouter "
                                                                                           "ce qu'il contient dans"
                                                                                           "le bon block.")
                for textline in textblock:
                    if textline.tag == "{http://www.loc.gov/standards/alto/ns-v4#}TextLine":
                        if textline.get("TAGREFS"):
                            pass
                        else:
                            for string in textline:
                                if string.tag == "{http://www.loc.gov/standards/alto/ns-v4#}String":
                                    for i in strings:
                                        if textline.get("ID") in i:
                                            propre = re.sub('" BASELINE', '" TAGREFS="' + tagref_default + '" BASELINE',
                                                                i)
                                            final += propre
                                        else:
                                            final += i