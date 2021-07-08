"""
Script de test permettant de vérifier l'adéquation du fichier XML_TEI au schéma RNG du projet
Author:Juliette Janes
Date: 26/03/2021
"""

from lxml import etree as ET


def association_xml_rng(schema_rng, document_xml):
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
    except etree.XMLSyntaxError:
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
        print("Le document XML n'est pas conforme au schéma TEI et à l'ODD du projet." + relaxng.assertValid(xml_tei_valide))

    return resultat


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

def get_entries(document):
    """
    Fonction qui permet pour un document précis, de vérifier que l'alto est construit de façon à ce que les TextBlocks
    entrées contiennent les TextLines correspondantes et que celles-ci ne sont pas contenues dans le TextBlock main.
    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)[0]
    textline_list = document.xpath("//alto:TextLine", namespaces=NS)
    for textline in textline_list:
        parent_textblock = textline.getparent()
        tagrefs_textblock = parent_textblock.attrib['TAGREFS']
        if tagrefs_textblock != tagref_entree:
            print("""
            L'entrée "+str(parent_textblock.attrib['ID'])+" n'est pas bien formée.""")
            action = input("""Voulez-vous revoir votre alto (1) ou
            passer outre (2). Attention le résultat risque d'oublier des entrées.""")
            if action == 1:
                sys.exit()
            else:
                pass

