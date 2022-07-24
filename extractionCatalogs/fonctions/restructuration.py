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

def correction_imbrication_segmentation(chemin_restructuration):
    # Restructuration des régions SEGMONTO :
    # Les positions HPOS, VPOS, Width et Height fonctionnent comme les régions iiif (même ordre et même dynamique) :
    # voici une documentation pour comprendre leur structure de représentation spatiale de la page :
    # https://iiif.io/api/image/2.1/#image-request-parameters
    Alto = ET.parse(chemin_restructuration)
    # dic pour stocker entrées vides et leurs régions :
    dic_zones_lignes = {}
    # une liste pour les lignes non traitées (vérification par l'utilisateur)
    lignes_MainZone = []
    lignes_MainZone_total = []
    # On récupère les TGAFREF :
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    # On vérifie s'il y a des "TextBlock" vides :
    if Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS):
        MainZone = Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS)[0]
    else:
        MainZone = None
    TextBlocks_vides = Alto.xpath("//alto:TextBlock[not(descendant::alto:TextLine)][not(@TAGREFS='{}')]".format(MainZone), namespaces=NS)
    if TextBlocks_vides:
        # On met un message concernant les entry et entryEnd, mais la fonction corrige l'imbrication de TOUS les textBlock :
        erreurs_nous_concernant = []
        if Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS):
            CustomZone_entry = Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
        else:
            CustomZone_entry = None
            if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entry), namespaces=NS):
                erreurs_nous_concernant.append("entry")
        if Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS):
            CustomZone_entryEnd = Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS)[0]
        else:
            CustomZone_entryEnd = None
            if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entryEnd), namespaces=NS):
                erreurs_nous_concernant.append("entryEnd")
        if erreurs_nous_concernant:
            erreurs_nous_concernant = str(erreurs_nous_concernant)
            erreurs_nous_concernant = erreurs_nous_concernant.replace(", ", " et ").replace("[", "").replace("]", "")
            print("\t  Des zones {} n'ont pas été saisies correctement sur eScriptorium et ne contiennent pas de texte dans le fichier ALTO produit".format(erreurs_nous_concernant))
        # On revient sur la fonction, qui corrige TOUS les problèmes d'imbrication de TextBlocks :
            # on créé un dictionnaire avec pour clés les ID de toutes les lignes du doc.
        # Ces clés réfèrent elles même à des dictionnaires contenant les zones de la ligne référée
        TextLines = Alto.xpath("//alto:TextLine", namespaces=NS)
        for TextLine in TextLines:
            TextLine_ID = TextLine.xpath("@ID", namespaces=NS)[0]
            HPOS_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@HPOS"), namespaces=NS)[0]
            VPOS_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@VPOS"), namespaces=NS)[0]
            WIDTH_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@WIDTH"), namespaces=NS)[0]
            HEIGHT_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@HEIGHT"), namespaces=NS)[0]
            # Un premier dictionnaire contient les zones pour une ligne :
            dic_zones_ligne = {}
            dic_zones_ligne["HPOS_L"] = HPOS_L
            dic_zones_ligne["VPOS_L"] = VPOS_L
            dic_zones_ligne["WIDTH_L"] = WIDTH_L
            dic_zones_ligne["HEIGHT_L"] = HEIGHT_L
            # Il est intégré à une deuxième dictionnaire qui contient des dictionnaires de zones pour chaque ligne :
            dic_zones_lignes[TextLine_ID] = dic_zones_ligne
        # Pour chaque entrée vide :
        for TextBlock in TextBlocks_vides:
            # On récupère les zones de l'entée
            TextBlock_ID = TextBlock.xpath("@ID", namespaces=NS)[0]
            HPOS_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@HPOS"), namespaces=NS)[0])
            VPOS_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@VPOS"), namespaces=NS)[0])
            WIDTH_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@WIDTH"), namespaces=NS)[0])
            HEIGHT_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@HEIGHT"), namespaces=NS)[0])
            # on appelle le dictionnaire de zones des lignes pour vérifier quelles lignes devraient être imbriquées dans quels TextBlocks :
            # ATTENTION : si les régions n'ont pas été saisies correctement sur escriptorium, cette fonction peut ne pas marcher
            # (Par exemple, quand quelqu'un dessine une ligne qui dépasse la zone entrée)
            for ligne_ID in dic_zones_lignes:
                HPOS_L = float(dic_zones_lignes[ligne_ID]["HPOS_L"])
                VPOS_L = float(dic_zones_lignes[ligne_ID]["VPOS_L"])
                WIDTH_L = float(dic_zones_lignes[ligne_ID]["WIDTH_L"])
                HEIGHT_L = float(dic_zones_lignes[ligne_ID]["HEIGHT_L"])
                # on augmente une marge d'erreur d'imbrication de 50 points, car il est usuel que les régions des lignes dépassent les TextBlock qui les contiennent.
                # Cela arrive quand les entrées sont serrées, eScriptorium établit automatiquement les zones de la ligne tracée par l'utilisateur, qui ne peut controler ce dépassement
                # Ce sont donc presque exclusivement les premières ou dernières lignes d'une entrée qui sont susceptible de ne pas rentrer dans le calcul. Le script prend en compte
                # Le fait que des lignes soient exclues et les indique dans le terminal, mais cette marge supplémentaire permet de corriger la très grande majorité des problèmes.
                # Cette marge est statistiquement adaptée aux catalogues traités par le codeur, il sera peut-être nécessaire de l'adapter à d'autres corpus ou qualités d'images.
                if HPOS_T <= HPOS_L + 60:
                    if VPOS_T <= VPOS_L + 60:
                        if HPOS_T + WIDTH_T + 60 >= HPOS_L + WIDTH_L:
                            if VPOS_T + HEIGHT_T + 60 >= VPOS_L + HEIGHT_L:
                                contenu = Alto.xpath("//alto:TextLine[@ID='{}']".format(ligne_ID), namespaces=NS)[0]
                                # et puisque on écrit une ligne dont l'ID existe déjà... l'ancienne disparaît automatiquement sur le fichier ALTO ! ;)
                                TextBlock.append(contenu)
        echec = 0
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entry), namespaces=NS):
            echec += 1
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entryEnd), namespaces=NS):
            echec += 1
        if echec >= 1:
            print("\t  Correction automatique : aucune ligne ne correspond aux zones vides")
        else :
            print("\t  Correction automatique : les lignes correspondant à des zones vides ont été déplacées vers ces zones")

        # pour vérifier sur le terminal quelles lignes sont contenues par quels TextBlocks :
                                #print("la ligne " + ligne + " se trouve dans l'entrée " + TextBlock_ID)
        # S'il reste des lignes directement dans des Textblock "MainZone", cela peut être une erreur. On les affichera dans le terminal pour que l'utilisateur puisse le déterminer :
        # C'est un problème récurant, puisque sur eScriptorium, l'utilisateur dessine des fois des lignes qui dépassent les entrées
        # On commence par récupérer l'ID de de "MainZone"
        if Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS):
            MainZone = Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS)[0]
        else:
            MainZone = None
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(MainZone), namespaces=NS):
            TextLine_dans_MainZone = Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(MainZone), namespaces=NS)
        else:
            TextLine_dans_MainZone = None
        # on récupère aussi le numéro de la page s'il existe ; il servira pour l'utilisateur comme guide pour la correction :
        if Alto.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS):
            NumberingZone = Alto.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS)[0]
        else:
            NumberingZone = None
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(NumberingZone), namespaces=NS):
            numero_page = Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(NumberingZone), namespaces=NS)[0]
            if TextLine_dans_MainZone:
                print("\t  ATTENTION : Les zones des lignes suivantes ne sont associées à aucune entry/entryEnd et n'ont pas été traitées , vérifiez l'extraction produite :"
                      "\n\t  [Les TextLine se situent directement dans des TextBlock 'Mainzone']")
                for TextLine in TextLine_dans_MainZone:
                    TextLine = TextLine + "(page {})".format(numero_page.replace("—", "").replace(" ", ""))
                    print("\t    " + TextLine)
                    lignes_MainZone.append(TextLine)
        # écriture du dossier :
        chemin_resegmentation = chemin_restructuration.replace("restructuration.xml", "resegmentation.xml")
        Alto.write(chemin_resegmentation, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    else:
        chemin_resegmentation = None
    return chemin_resegmentation, lignes_MainZone