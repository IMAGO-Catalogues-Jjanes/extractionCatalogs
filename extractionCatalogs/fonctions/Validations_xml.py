"""
Script de test permettant de vérifier l'adéquation du fichier XML_TEI au schéma RNG du projet
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

from lxml import etree as ET
import re
import sys
from urllib.request import urlopen
from extractionCatalogs.variables.contenu_TEI import lien_schema


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
    # on vérifie dans un premier temps s'il est bien formé en xml :
    except ET.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme :
        print("\t– Le fichier xml n'est pas bien formé.")
        return
    # récupération et parsage du fichier rng du projet (lien_schema est une variable importée) :
    # si le lien a été indiqué dans le gabarit du projet :
    if lien_schema:
        schema = urlopen(lien_schema)
    # si non, on utilise le schéma intégré en local (schema du projet IMAGO, il peut être remplacé par un autre) :
    else:
        schema = "extractionCatalogs/variables/validation_alto/out/ODD_VisualContagions.rng"
    relaxng_fichier = ET.parse(schema)
    # Si l'on préfère utiliser le document en local :
    # relaxng_fichier = ET.parse("extractionCatalogs/fonctions/validation_alto/out/ODD_VisualContagions.rng")
    relaxng = ET.RelaxNG(relaxng_fichier)
    # association du relaxng et du fichier tei
    if relaxng(fichier_xml):
        # s'il est conforme, la terminal l'indique. Cela n'arrivera que dans les cas où les ALTO en input ont été
        # parfaitement encodés et corrigés préalablement
        resultat= "tei valide"
        print("\t– Le document XML produit est conforme au schéma TEI et à l'ODD du projet.")
    else:
        # on signale que le document n'est pas valide. Ce sera le cas dans la très grande majorité des cas,
        # et il est normal de devoir faire des corrections manuelles pour compléter l'extraction automatique
        print("\t– Le document XML produit n'est pas conforme au schéma TEI et à l'ODD du projet ; il nécessite des corrections manuelles ")
        resultat= "tei non valide"
    return resultat

def structure_alto(chemin_document):
    """
    Fonction qui permet pour un document précis, de vérifier que l'alto est construit de façon à ce que les TextBlocks
    entrées contiennent les TextLines correspondantes et que celles-ci ne sont pas directement contenues dans le
    TextBlock main. Cela impossibilite en effet l'extraction. La structure attendue est :
    Layout > Page > PrintSpace > TextBlock (entry) > TextLine > String
    et non pas
    Layout > Page > PrintSpace > TextBlock (MainZone) > TextLine > String

    :param document: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    document = ET.parse(chemin_document)
    # liste de toutes les TAGREFS :
    tagrefs_list = document.xpath("//alto:OtherTag/@ID", namespaces=NS)
    # liste de éléments TextLine :
    textline_list = document.xpath("//alto:TextLine", namespaces=NS)

    # === On récupère les éléments de l'ontologie segmonto, s'ils existent ===
    # Note : ce script devra être adapté à l'évolution de l'ontologie, qui se trouve en phase de développement.
    # Il faudra notamment l'adapter à la complexification des noms des balises qui comportent maintenant des options des précision.
    # Si le terminal signal un élément de l'ontologie comme n'en faisant pas partie, il faut l'ajouter ici.

    # On récupère l'ID du type de balise CustomZone:entry :
    if document.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS):
        tagref_entree = document.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
    else:
        tagref_entree = None
    # On récupère l'ID du type de balise MainZone :
    if document.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS):
        MainZone = document.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS)[0]
    else:
        MainZone = None
    # On récupère l'ID du type de balise EntryEnd :
    if document.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS):
        EntryEnd = document.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS)[0]
    else:
        EntryEnd = None
    # On récupère l'ID du type de balise "NumberingZone" :
    if document.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS):
        NumberingZone = document.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS)[0]
    else:
        NumberingZone = None
    # On récupère l'ID du type de balise "GraphicZone: illustration" :
    if document.xpath("//alto:OtherTag[@LABEL='GraphicZone:illustration']/@ID", namespaces=NS):
        GraphicZone_illustration = document.xpath("//alto:OtherTag[@LABEL='GraphicZone:illustration']/@ID", namespaces=NS)[0]
    else:
        GraphicZone_illustration = None
    # On récupère l'ID du type de balise "GraphicZone:ornamentation" :
    if document.xpath("//alto:OtherTag[@LABEL='GraphicZone:ornamentation']/@ID", namespaces=NS):
        GraphicZone_ornamentation = document.xpath("//alto:OtherTag[@LABEL='GraphicZone:ornamentation']/@ID", namespaces=NS)[0]
    else:
        GraphicZone_ornamentation = None
    # On récupère l'ID du type de balise "StampZone" :
    if document.xpath("//alto:OtherTag[@LABEL='StampZone']/@ID", namespaces=NS):
        StampZone = document.xpath("//alto:OtherTag[@LABEL='StampZone']/@ID", namespaces=NS)[0]
    else:
        StampZone = None
    # On récupère l'ID du type de balise "QuireMarksZone" :
    if document.xpath("//alto:OtherTag[@LABEL='QuireMarksZone']/@ID", namespaces=NS):
        QuireMarksZone = document.xpath("//alto:OtherTag[@LABEL='QuireMarksZone']/@ID", namespaces=NS)[0]
    else:
        QuireMarksZone = None
    # On récupère l'ID du type de balise "MarginTextZone" :
    if document.xpath("//alto:OtherTag[@LABEL='MarginTextZone']/@ID", namespaces=NS):
        MarginTextZone = document.xpath("//alto:OtherTag[@LABEL='MarginTextZone']/@ID", namespaces=NS)[0]
    else:
        MarginTextZone = None
    # On récupère l'ID du type de balise "TitlePageZone" :
    if document.xpath("//alto:OtherTag[@LABEL='TitlePageZone']/@ID", namespaces=NS):
        TitlePageZone = document.xpath("//alto:OtherTag[@LABEL='TitlePageZone']/@ID", namespaces=NS)[0]
    else:
        TitlePageZone = None
    # On récupère l'ID du type de balise "DropCapitalZone" :
    if document.xpath("//alto:OtherTag[@LABEL='DropCapitalZone']/@ID", namespaces=NS):
        DropCapitalZone = document.xpath("//alto:OtherTag[@LABEL='DropCapitalZone']/@ID", namespaces=NS)[0]
    else:
        DropCapitalZone = None
    # On récupère l'ID du type de balise "DamageZone" :
    if document.xpath("//alto:OtherTag[@LABEL='DamageZone']/@ID", namespaces=NS):
        DamageZone = document.xpath("//alto:OtherTag[@LABEL='DamageZone']/@ID", namespaces=NS)[0]
    else:
        DamageZone = None
    # On récupère l'ID du type de balise "DigitizationArtefactZone" :
    if document.xpath("//alto:OtherTag[@LABEL='DigitizationArtefactZone']/@ID", namespaces=NS):
        DigitizationArtefactZone = document.xpath("//alto:OtherTag[@LABEL='DigitizationArtefactZone']/@ID", namespaces=NS)[0]
    else:
        DigitizationArtefactZone = None
    # On récupère l'ID du type de balise "GraphicZone" :
    if document.xpath("//alto:OtherTag[@LABEL='GraphicZone']/@ID", namespaces=NS):
        GraphicZone = document.xpath("//alto:OtherTag[@LABEL='GraphicZone']/@ID", namespaces=NS)[0]
    else:
        GraphicZone = None
    # On récupère l'ID du type de balise "MusicZone" :
    if document.xpath("//alto:OtherTag[@LABEL='MusicZone']/@ID", namespaces=NS):
        MusicZone = document.xpath("//alto:OtherTag[@LABEL='MusicZone']/@ID", namespaces=NS)[0]
    else:
        MusicZone = None
    # On récupère l'ID du type de balise "TableZone" :
    if document.xpath("//alto:OtherTag[@LABEL='TableZone']/@ID", namespaces=NS):
        TableZone = document.xpath("//alto:OtherTag[@LABEL='TableZone']/@ID", namespaces=NS)[0]
    else:
        TableZone = None

    # pour chaque objet dans cette liste :
    textline_dans_MainZone = 0
    textline_dans_autre = 0
    for textline in textline_list:
        # on récupère le TextBlock parent pour chaque TextLine :
        parent_textblock = textline.getparent()
        n_zone_non_entree = 0
        try:
            # On récupère le TAGREF de ce TextBlock, qui devrait presque toujours correspondre à une "CustomZone:entry"
            # Des fois, le TAGFREF peut correspondre à une "CustomZone:entryEnd", à une "NumberingZone", ou autres
            tagrefs_textblock = parent_textblock.attrib['TAGREFS']
            # Dans les cas ou l'ID du TextBLock correspond à un autre type d'entrée qu'une "CustomZone:entry"  :
            if tagrefs_textblock != tagref_entree:
                # Si le TAGREF du TextBlock est une MainZone, cela veut dire que l'imbrication est fautive :
                if tagrefs_textblock == MainZone:
                    # on augmente un compteur qu'on utilisera après pour énumérer ce type de problème :
                    textline_dans_MainZone += 1
                # Si le tagref est associé à un autre élément de l'ontologie Segmonto, on estime qu'il n'y a pas de problème :
                # (dernière vérification de conformité à l'ontologie effectuée en aout 2022)
                elif tagrefs_textblock == EntryEnd:
                    pass
                elif tagrefs_textblock == NumberingZone:
                    pass
                elif tagrefs_textblock == GraphicZone_illustration:
                    pass
                elif tagrefs_textblock == GraphicZone_ornamentation:
                    pass
                elif tagrefs_textblock == StampZone:
                    pass
                elif tagrefs_textblock == QuireMarksZone:
                    pass
                elif tagrefs_textblock == MarginTextZone:
                    pass
                elif tagrefs_textblock == TitlePageZone:
                    pass
                elif tagrefs_textblock == DropCapitalZone:
                    pass
                elif tagrefs_textblock == DamageZone:
                    pass
                elif tagrefs_textblock == DigitizationArtefactZone:
                    pass
                elif tagrefs_textblock == GraphicZone:
                    pass
                elif tagrefs_textblock == MusicZone:
                    pass
                elif tagrefs_textblock == TableZone:
                    pass
                # Si le TAGREF se trouve dans la liste de tous les TAGREFS, est n'est pas associé à l'ontologie segmonto
                # (puisqu'on à filtré préalablement les éléments Segmonto)
                elif tagrefs_textblock in tagrefs_list:
                    textline_dans_autre += 1
                    n_zone_non_entree += 1
        except:
            #print("\t  L'entrée " + str(parent_textblock.attrib['ID']) + " n'a pas d'attribut TAGREF défini")
            pass
    if textline_dans_MainZone >= 1:
        print("\t  Les <TextLine> de l'objet " + str(parent_textblock.attrib['ID']) + " se trouvent directement dans une 'MainZone'")
    if textline_dans_autre >= 1:
        print("\t  L'élément " + str(parent_textblock.attrib['ID']) + " n'est pas associé à l'ontologie Segmonto")
    return textline_dans_MainZone, textline_dans_autre


def formation_alto(fichier):
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
    # On récupère l'ID du type de balise "HeadingLine", qui est aussi présent dans le projet :
    if file.xpath("//alto:OtherTag[@LABEL='HeadingLine']/@ID", namespaces=NS):
        HeadingLine = file.xpath("//alto:OtherTag[@LABEL='HeadingLine']/@ID", namespaces=NS)[0]
    else:
        HeadingLine = None
    # On récupère l'ID du type de balise "CustomLine", qui peut aussi être présent dans le projet :
    if file.xpath("//alto:OtherTag[@LABEL='CustomLine']/@ID", namespaces=NS):
        CustomLine = file.xpath("//alto:OtherTag[@LABEL='CustomLine']/@ID", namespaces=NS)[0]
    else:
        CustomLine = None
    # On récupère l'ID du type de balise "DropCapitalLine", qui peut aussi être présent dans le projet :
    if file.xpath("//alto:OtherTag[@LABEL='DropCapitalLine']/@ID", namespaces=NS):
        DropCapitalLine = file.xpath("//alto:OtherTag[@LABEL='DropCapitalLine']/@ID", namespaces=NS)[0]
    else:
        DropCapitalLine = None
    if file.xpath("//alto:OtherTag[@LABEL='InterlinearLine']/@ID", namespaces=NS):
        InterlinearLine = file.xpath("//alto:OtherTag[@LABEL='InterlinearLine']/@ID", namespaces=NS)[0]
    else:
        InterlinearLine = None
    if file.xpath("//alto:OtherTag[@LABEL='MusicLine']/@ID", namespaces=NS):
        MusicLine = file.xpath("//alto:OtherTag[@LABEL='MusicLine']/@ID", namespaces=NS)[0]
    else:
        MusicLine = None

    # TODO pourquoi la méthode append() ne marche pas ici dans les itérations qui suivent pour la liste problemes ?
    # TODO c'est les objets etree qui posent problème pour cela ? les variables probleme* sont imprimées comme attendu
    # TODO mais l'append semble n'avoir lieu qu'après la fin de l'ensemble des itérations et non pas une après l'autre, donc la liste reste vide
    # Deux possibilités, liste ou dic, aucune ne marche pour l'instant :
    problemes = []
    problemes_dic = {}
    # === 1. On s'occupe des TextBlock ===
    # pour chaque balise page
    for page in layout:
        # pour chaque balise printspace contenue dans les page
        for printspace in page:
            # pour chaque balise textblock contenue dans les printspace
            for textblock in printspace:
                # on vérifie si des textblock sont mal ou pas référencées
                # (le script les mets de côté, il est donc important de vérifier s'ils contiennent des informations à extraire)
                if textblock.get("ID") == "eSc_dummyblock_":
                    probleme1 = "\t L'élément TextBlock '" + textblock.get("ID") + \
                                " n'est pas conforme à l'ontologie du projet. " + \
                                "\n\t  S'il contient des informations à extraire, il faut le supprimer et mettre le contenu dans un TextBlock conforme."
                    problemes.append(probleme1)
                    problemes_dic[textblock.get("ID")] = probleme1
                    print(probleme1)
                elif textblock.get("TAGREFS") == None:
                    probleme2 = "\t  Le fichier contient une balise TextBlock '" + textblock.get("ID") + \
                                "' sans TAGREF, donc non associé à l'ontologie du projet."
                    problemes.append(probleme2)
                    print(probleme2)
                elif textblock.get("TAGREFS") == "BT":
                    probleme3 = "\t  Le fichier contient une balise TextBlock '" + textblock.get("ID") + \
                                "' dont l'attribut TAGREF est incomplet. " + \
                                "\n\t  S'il contient des informations à extraire, il faut le compléter pour l'associer à l'ontologie du projet."
                    problemes.append(probleme3)
                    print(probleme3)
    # === 2. On s'occupe des TextLine ===
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
                        elif textline.get("TAGREFS") == HeadingLine:
                            pass
                        elif textline.get("TAGREFS") == CustomLine:
                            pass
                        elif textline.get("TAGREFS") == DropCapitalLine:
                            pass
                        elif textline.get("TAGREFS") == InterlinearLine:
                            pass
                        elif textline.get("TAGREFS") == MusicLine:
                            pass
                        # autrement, on le signale dans le terminal
                        else:
                            probleme4 = "\t  le fichier contient une balise TextLine '" + textline.get("ID") + \
                                        "' sans TAGREF correspondant à l'ontologie du projet."
                            problemes.append(probleme4)
                            print(probleme4)
    # TODO la liste retournée est vide !
    return problemes
