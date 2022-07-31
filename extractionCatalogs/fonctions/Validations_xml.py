"""
Script de test permettant de faire des vérifications xml :
- conformité au schéma rng du projet
- conformité à l'ontologie Segmonto


Author:
Esteban Sánchez Oeconomo, 2022
Juliette Janès, 2021
"""

from lxml import etree as ET
import re
import sys
from urllib.request import urlopen
from extractionCatalogs.variables.contenu_TEI import lien_schema


def association_xml_rng(document_xml):
    """ Fonction qui vérifie la conformité du XML-TEI produit au schéma rng du projet en cours. Ce schéma doit être
    indiqué dans le dossier variables, dans le gabarit du projet en cours.

    :param schema_rng: schéma RelaxNG comprenant la structure définie dans l'ODD du projet
    :type schema_rng: str
    :param document_xml: fichier XML TEI parsé par etree
    :type document_xml: str
    :return resultat: chaîne de caractères validant le fichier XML TEI
    :type resultat:str
    """
    # on parse le document xml pour le récupérer
    try:
        fichier_xml = ET.parse(document_xml)
    # on vérifie dans un premier temps s'il est bien formé en xml :
    except ET.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme :
        print("\t[!] Le fichier xml n'est pas bien formé.")
        return
    # récupération et parsage du fichier rng du projet (lien_schema est une variable importée) :
    # si le lien a été indiqué dans le gabarit du projet :
    try:
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
            # parfaitement encodés / préalablement corrigés
            print("\t✓ Le document XML produit est conforme au schéma TEI et à l'ODD du projet.")
        else:
            # on signale que le document n'est pas valide. Ce sera le cas dans la très grande majorité des cas,
            # et il est normal de devoir faire des corrections manuelles pour compléter l'extraction automatique
            print("\t[!] Le document produit nécessite des corrections manuelles"
                  "\n\t    [Le fichier XML produit n'est pas conforme au schéma TEI et à l'ODD du projet]")
    except :
        print("\t[!] vérification de la conformité XML impossible : vous n'êtes pas connecté à internet")
    return None


def conformite_Segmonto(chemin_document):
    """
    Segmonto est un standard de nommage des zones d'une page d'imprimé. Voir : https://github.com/SegmOnto

    Cette fonction :
    - Vérifie que les éléments TextBlock d'un fichier XML Alto sont associés à des noms correspondant à l'ontologie Segmonto
    - Vérifie aussi combien d'éléments TextLine sont directement situés dans des TextBlock "MainZone", puisque cela
      peut constituer une erreur de saisie.
    - Établit une liste de problèmes de conformité des éléments à l'ontologie Segmonto.

    Note :  CE SCRIPT NE TRAITE PAS TOUS LES CAS D'USAGE DE L'ONTOLOGIE, ET SE LIMITE À CEUX QUI CORRESPONDENT AU PROJET COURANT
    Il devra être adapté à l'évolution de l'ontologie, qui se trouve en phase de développement.
    Il faudra notamment l'adapter à la complexification des noms des balises qui comportent maintenant la possibilité
    de préciser leur contenu.

    :param fichier: fichier XML ALTO 4 parsé produit par l'OCR et contenant la transcription d'une page de catalogue
    :return problemes:
    :type problemes: list
    :return textline_dans_MainZone: compteur de lignes directement contenues dans des TextBlock 'MainZone'
    :type textline_dans_MainZone: int
    :return textline_dans_autre: compteur de lignes contenues dans des TextBlock non associés à l'ontologie Segmonto
    :type textline_dans_autre: int
    """
    # === 1. on créé les variables initiales ===
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    document = ET.parse(chemin_document)
    root = document.getroot()
    # on récupère le nom du fichier pouer les messages d'erreur
    fileName = document.xpath("//alto:fileName/text()", namespaces=NS)[0]
    # liste de toutes les ID de Tag, qui réfèrent à des noms données aux zones d'une page (ex: "CustomZone:entry", "MainZone", etc.)
    tagrefs_list = document.xpath("//alto:OtherTag/@ID", namespaces=NS)
    # liste de éléments TextLine :
    textline_list = document.xpath("//alto:TextLine", namespaces=NS)
    # on selectionne le troisième ensemble de balises du fichier, appelé "layout", et on va boucler sur chaque niveau
    layout = root[2]

    # === 2. On récupère les ID des noms des zones de l'ontologie Segmonto, s'ils existent ===
    # === 2.1 ID des types de zone Segmonto ===
    # On récupère l'ID du type de balise CustomZone:entry :
    # si le chemin xpath vers l'ID de ce nom existe :
    if document.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS):
        # une variable appelée comme la balise contiendra en valeur l'ID
        CustomZone_entry = document.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
    else:
        CustomZone_entry = None
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
    # On récupère l'ID du type de balise "RunningTitleZone" :
    if document.xpath("//alto:OtherTag[@LABEL='RunningTitleZone']/@ID", namespaces=NS):
        RunningTitleZone = document.xpath("//alto:OtherTag[@LABEL='RunningTitleZone']/@ID", namespaces=NS)[0]
    else:
        RunningTitleZone = None

    # === 2.2 ID des types de ligne Segmonto ===
    # on récupère l'identifiant des 'DefaultLine', associés à des éléments TextLine
    if document.xpath("//alto:OtherTag[@LABEL='DefaultLine']/@ID", namespaces=NS):
        tagref_default = document.xpath("//alto:OtherTag[@LABEL='DefaultLine']/@ID", namespaces=NS)[0]
    else:
        tagref_default = None
    # On récupère l'ID du type de ligne 'HeadingLine', qui est aussi présent dans le projet :
    if document.xpath("//alto:OtherTag[@LABEL='HeadingLine']/@ID", namespaces=NS):
        HeadingLine = document.xpath("//alto:OtherTag[@LABEL='HeadingLine']/@ID", namespaces=NS)[0]
    else:
        HeadingLine = None
    # On récupère l'ID du type de ligne "CustomLine", qui peut aussi être présent dans le projet :
    if document.xpath("//alto:OtherTag[@LABEL='CustomLine']/@ID", namespaces=NS):
        CustomLine = document.xpath("//alto:OtherTag[@LABEL='CustomLine']/@ID", namespaces=NS)[0]
    else:
        CustomLine = None
    # On récupère l'ID du type de ligne "DropCapitalLine", qui peut aussi être présent dans le projet :
    if document.xpath("//alto:OtherTag[@LABEL='DropCapitalLine']/@ID", namespaces=NS):
        DropCapitalLine = document.xpath("//alto:OtherTag[@LABEL='DropCapitalLine']/@ID", namespaces=NS)[0]
    else:
        DropCapitalLine = None
    # On récupère l'ID du type de ligne "InterlinearLine", qui peut aussi être présent dans le projet :
    if document.xpath("//alto:OtherTag[@LABEL='InterlinearLine']/@ID", namespaces=NS):
        InterlinearLine = document.xpath("//alto:OtherTag[@LABEL='InterlinearLine']/@ID", namespaces=NS)[0]
    else:
        InterlinearLine = None
    # On récupère l'ID du type de ligne "MusicLine" ; il n'est pas présent dans le projet mais fait partie de Segmonto ; on couvre ainsi toutes les possibilités
    if document.xpath("//alto:OtherTag[@LABEL='MusicLine']/@ID", namespaces=NS):
        MusicLine = document.xpath("//alto:OtherTag[@LABEL='MusicLine']/@ID", namespaces=NS)[0]
    else:
        MusicLine = None

    # === 3. on créé les compteurs  ===
    # compteur pour signaler le nombre d'éléments TextLines contenus dans des TextBlock "MainZone"
    textline_dans_MainZone = 0
    # compteur pour signaler le nombre d'éléments TextLines contenus dans des TextBlock dont le nom ne correspond pas à l'ontologie Segmonto
    textline_dans_autre = 0
    # pour chaque objet dans la liste avec toutes les TextLines du document :
    for textline in textline_list:
        # on récupère le TextBlock parent pour chaque TextLine :
        parent_textblock = textline.getparent()
        try:
            # On récupère l'attribut TAGREFS du TextBlock parent ; cet attribut fait référence à un ID de TAG,
            # c'est à dire qu'il permet de savoir comment nommer la zone (on devrait avoir à faire à des "CustomZone:entry"
            # dans la très grande majorité des cas, et en moindre mesure des "CustomZone:entryEnd", "MainZone", "NumberingZone")
            tagrefs_textblock = parent_textblock.attrib['TAGREFS']
            # Dans les cas ou l'ID du TextBLock correspond à un autre type d'entrée qu'une "CustomZone:entry"  :
            if tagrefs_textblock != CustomZone_entry:
                # Si le TAGREF du TextBlock est une MainZone, cela veut dire que l'imbrication est peut-être érronnée.
                # en effet, "MainZone" fait référence à tout l'espace sémantique de la page et ne devrait pas contenir directement des TextLine,
                # lequelles doivent être contenues dans d'autres zones plus spécifiques
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
                elif tagrefs_textblock == RunningTitleZone:
                    pass
                # Mais si le TAGREFS se trouve dans la liste de tous les ID, et qu'il n'est pas associé à l'ontologie segmonto,
                # on considère que le document n'est pas conforme à l'ontologie.
                elif tagrefs_textblock in tagrefs_list:
                    textline_dans_autre += 1
        except:
            pass
        if textline_dans_autre >= 1:
            print("\t  [!] L'élément TextBLock '" + str(
                parent_textblock.attrib['ID']) + "' n'est pas associé à l'ontologie Segmonto")

    # === 4. Messages explicitant les problèmes ===
    # on établit une liste qui sera retournée, et qui sera utilisée pour mettre les messages dans le fichier problemes.txt
    problemes = []
    # === 4.1 On s'occupe des TextLine ===
    for page in layout:
        # pour chaque balise PrintSpace contenue dans les Page
        for printspace in page:
            # pour chaque balise TextBlock contenue dans les PrintSpace
            for textblock in printspace:
                # pour chaque balise contenue dans les TextBlock
                for textline in textblock:
                    # si la balise est TextLine (puisqu'il peut y en avoir d'autres...)
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
                            probleme3 = "\t   [!] le fichier {} contient une ligne (TextLine ID='".format(
                                fileName) + textline.get("ID") + \
                                        "') non conforme à l'ontologie Segmonto. [voir attribut TAGREFS]"
                            problemes.append(probleme3)
                            print(probleme3)

        # === 4.2 On s'occupe des TextBlock ===
        # pour chaque balise Page
        for page in layout:
            # pour chaque balise PrintSpace contenue dans les Page
            for printspace in page:
                # pour chaque balise TextBlock contenue dans les PrintSpace
                for textblock in printspace:
                    # on vérifie si des TextBlock sont mal ou pas référencés
                    # (le script les mets de côté, il est donc important de vérifier s'ils contiennent des informations à extraire)
                    if textblock.get("ID") == "eSc_dummyblock_":
                        probleme1 = "\t   [!] L'élément TextBlock (ID='" + textblock.get("ID") + \
                                    ") du fichier {} n'est pas conforme à l'ontologie Segmonto. ".format(fileName)
                        problemes.append(probleme1)
                        print(probleme1)

                    correspondances = None
                    for ID in tagrefs_list:
                        if textblock.get("TAGREFS") == ID:
                            correspondances = True
                    if correspondances == None:
                        probleme2 = "\t   [!] Le fichier {} contient un élément TextBlock (ID='".format(
                            fileName) + textblock.get("ID") + \
                                    "') qui n'est pas associé à l'ontologie Segmonto. [voir attribut TAGREFS]"
                        problemes.append(probleme2)
                        print(probleme2)

    return textline_dans_MainZone, textline_dans_autre, problemes