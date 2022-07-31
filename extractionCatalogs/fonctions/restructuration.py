import os
import click
import re
from lxml import etree as ET
import errno

def restructuration_automatique(directory, fichier, extraction_directory):
    """ Fonction permettant, pour chaque fichier d'un dossier donné, de lui appliquer la feuille de transformation
    transformation_alto.xsl qui remet dans le bon ordre les élémements de l'output alto de eScriptorium.
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
    transformation_xslt = ET.XSLT(ET.parse("./extractionCatalogs/fonctions/Restructuration_alto.xsl"))
    propre = transformation_xslt(original)
    # on créé un nouveau fichier dans le dossier résultat
    chemin_restructuration = extraction_directory + "/restructuration ALTO/" + fichier[:-4] + "_restructuration.xml"
    os.makedirs(os.path.dirname(chemin_restructuration), exist_ok=True)
    with open(chemin_restructuration, mode='wb') as f:
        f.write(propre)
    return chemin_restructuration

def correction_imbrication_segmentation(chemin_restructuration):
    ''' Cette fonction permet de corriger les erreurs d'imbrication des éléments d'un fichier Alto en output d'eScriptorium,
    selon leur position dans la page.
    Elle localise tous les éléments "TextBlock" (régions) vides, puis toutes les "TextLine" (lignes comportant du texte)
    du fichier, et calcule leurs positions dans l'image pour déterminer si ils sont liés.
    L'intérêt de cette fonction dépasse le projet en cours et répond à un problème constaté dans l'interface eScriptorium :
    selon l'odre de saisie des regions par l'utilisateur, le document ALTO en output effectue des imbrications variables
    qui peuvent être problématiques. Souvent, des TextLine qui devraient être contenues par des TextBlock spécifiques
    vont être contenues directement dans un TextBlock plus englobant, c'est à dire dans un ordre hiérarchique  érronné
    (on peut penser à une série de poupées russes dans laquelle il manquerait des poupées, qui seraient laissées vides
    et à côté de l'ensemble).

    Dans notre cas, le problème est que souvent des TextBlock "CustomZone:entry" sont laissées vides, et les TextLines
    concernées sont contenues directement dans des TextBlock "MainZone" qui servent à signaler tout l'espace sémantique
    de la page. Une construction correcte consiste en des TextBlock "CustomZone:entry" contenant des "TextLine",
    et un TextBLock "MainZone" vide.

    Si la fonction est adaptée au projet Artl@s (ontologie Segmonto avec zones adaptées au projet),
    elle a été conçue pour mettre en ordre TOUT fichier Alto mal imbriqué.

    Le calcul des positions dans l'image est fait à partir des attributs HPOS, VPOS, WIDTH et HEIGHT, Systématiquement
    renseignés pour tous les TextBlocks et TextLines. Ces données fonctionnent comme les régions iiif
    (même ordre et mème découpage de l'image), dont la documentation est très utile pour en comprendre la dynamique :
    https://iiif.io/api/image/2.1/#image-request-parameters

    Esteban Sánchez Oeconomo, 2022

    :param chemin_restructuration: chemin vers un fichier Alto issue de eScriptorium
    :type chemin_restructuration: str
    :return chemin_resegmentation: chemin vers le fichier corrigé
    :return lignes_MainZone: liste de chaînes de caractères contenues par des "TextLine" qui après le calcul
    ne correspondent à aucun autre TextBlock que "MainZone". L'utilisateur doit déterminer si ce sont des lignes mal
    extraites, ou bien des lignes sans vocation à être intégrées dans un TextBlock spécifique.
    '''
    # === 1. On établit les variables initiales ===
    # on commence par parser un fichier alto en entrée :
    Alto = ET.parse(chemin_restructuration)
    # dictionnaire pour stocker tous les TextBlock vides et leurs données concernant leur position dans la page :
    dic_zones_lignes = {}
    # liste pour stocker les TextLine non traitées :
    # (si après le calcul, elles ne correspondent à aucun TextBlock autre que "MainZone")
    lignes_MainZone = []
    # d'abord, une variable contenant l'espace de nom alto et qui servira à faire toutes nos recherches xpath :
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    # des compteurs qui nous permettront de signaler le nombre de lignes et de zones corrigées :
    TextLines_corriges = 0
    TextBlocks_corriges = 0
    # On récupère les TGAFREF, c'est à dire des identifiants qui réfèrent au "LABEL" assigné au TextBLock ("Mainzone", "CustomZone:entry", etc.) :
    # s'il existe, on récupère le TAGREF permettant d'identifier le TextBlock "MainZone" dans la page :
    if Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS):
        MainZone = Alto.xpath("//alto:OtherTag[@LABEL='MainZone']/@ID", namespaces=NS)[0]
    else:
        MainZone = None
    # on vérifie s'il y a des "TextBlock" vides, qui ne soient pas des "MainZone" (seul TextBlock censé être vide) :
    TextBlocks_vides = Alto.xpath("//alto:TextBlock[not(descendant::alto:TextLine)][not(@TAGREFS='{}')]".format(MainZone), namespaces=NS)
    # s'il y a des "TextBlock" vides qui ne soient pas des "MainZone" :

    # === 2. On signale les problèmes relatifs à notre projet : "entry" et "entryEnd" vides ===
    if TextBlocks_vides:
        print("\t      Le Ficher Alto produit par eScriptorium contient des zones ['TextBLock'] vides")
        # le terminal indique des messages relatifs aux TextBlock "CustomZone:entry" et "CustomZone:entryEnd", spécifiques
        # à notre projet ; mais la fonction corrige l'imbrication de TOUS les TextBlocks vides n'étant pas des "MainZone" :
        # liste pour ajouter ajouter "entry" et "entryEnd" si des TextBlock concernés sont vides :
        erreurs_nous_concernant = []
        # s'il existe, on récupère le TAGREF permettant d'identifier les TextBlock "CustomZone:entry" dans la page :
        if Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS):
            CustomZone_entry = Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
        else:
            CustomZone_entry = None
        # S'il y a des TextBlock "CustomZone:entry" vides, on ajoute "entry" à la liste (une seule fois pour l'ensemble) :
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entry), namespaces=NS):
            erreurs_nous_concernant.append("CustomZone:entry")
        # s'il existe, on récupère le TAGREF permettant d'identifier les TextBlock "CustomZone:entryEnd" dans la page :
        if Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS):
            CustomZone_entryEnd = Alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS)[0]
        else:
            CustomZone_entryEnd = None
        # S'il y a des TextBlock "CustomZone:entryEnd" vides, on ajoute "entryEnd" à la liste (une seule fois pour l'ensemble) :
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}'][not(descendant::alto:TextLine)]".format(CustomZone_entryEnd), namespaces=NS):
            erreurs_nous_concernant.append("CustomZone:entryEnd")
        # si la liste n'est pas vide, on la transforme en chaîne, on la nettoie et on l'utilise pour indiquer sur le
        # terminal qu'il y a des problèmes d'imbrication concernant notre projet :
        if erreurs_nous_concernant:
            erreurs_nous_concernant = str(erreurs_nous_concernant)
            erreurs_nous_concernant = erreurs_nous_concernant.replace(", ", " et des ").replace("[", "").replace("]", "")
            print("\t      – Parmi ces zones ['TextBlock'] vides, il y a des {}".format(erreurs_nous_concernant))

        # on revient sur la fonction à proprement parler, qui associe à TOUS les TextBlocks vides les TextLines qui les concernent:

        # === 3. On traite les les TextLine du document ===
        # on récupère toutes les TextLines du document, mais on met de côté celles dont les TextBlock parent sont des
        # NumberingZone, puisqu'elles nous concernent pas et que même si le script les ignore normalement,
        # la marge d'erreur qu'on établira plus tard pour calculer les positions dans la page peut dans certain cas
        # les considérer comme faisant partie d'une entrée
        TextLines = Alto.xpath("//alto:TextBlock[not(@TAGREFS='BT8')]/alto:TextLine", namespaces=NS)
        # pour chacune d'entre elles :
        for TextLine in TextLines:
            # on récupère l'ID de la TextLine courante, et on l'utilise pour construire le chemin xpath vers les
            # attributs qui signalent sa position dans la page :
            TextLine_ID = TextLine.xpath("@ID", namespaces=NS)[0]
            # HPOS = Horizontal Position
            HPOS_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@HPOS"), namespaces=NS)[0]
            # VPOS = Vertical Position
            VPOS_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@VPOS"), namespaces=NS)[0]
            # WIDTH = largeur
            WIDTH_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@WIDTH"), namespaces=NS)[0]
            # HEIGHT = hauteur
            HEIGHT_L = Alto.xpath("//alto:TextLine[@ID='{}']/{}".format(TextLine_ID, "@HEIGHT"), namespaces=NS)[0]
            # Un premier dictionnaire contient les zones associées à la ligne courante :
            dic_zones_ligne = {}
            dic_zones_ligne["HPOS_L"] = HPOS_L
            dic_zones_ligne["VPOS_L"] = VPOS_L
            dic_zones_ligne["WIDTH_L"] = WIDTH_L
            dic_zones_ligne["HEIGHT_L"] = HEIGHT_L
            # Il est intégré à une deuxième dictionnaire qui contient des dictionnaires de zones pour chaque ligne :
            dic_zones_lignes[TextLine_ID] = dic_zones_ligne

        # === 3. On traite les les TextBlock vides du document ===
        # Pour chaque entrée vide :
        for TextBlock in TextBlocks_vides:
            # on récupère l'ID du TextBlock courant, et on l'utilise pour construire le chemin xpath vers les
            # attributs qui signalent sa position dans la page :
            TextBlock_ID = TextBlock.xpath("@ID", namespaces=NS)[0]
            # on utilise float et non pas int pour convertir les chiffres car les données peuvent contenir des décimales :
            HPOS_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@HPOS"), namespaces=NS)[0])
            VPOS_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@VPOS"), namespaces=NS)[0])
            WIDTH_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@WIDTH"), namespaces=NS)[0])
            HEIGHT_T = float(Alto.xpath("//alto:TextBlock[@ID='{}']/{}".format(TextBlock_ID, "@HEIGHT"), namespaces=NS)[0])

            # === 4. On calcule quelles TextLignes sont associées à quels TextBLocks vides ===
            # ATTENTION : si les régions n'ont pas été saisies correctement sur escriptorium, cette fonction est susceptible de ne pas marcher.
            # Ceci arrive par exemple quand quelqu'un dessine une ligne qui dépasse le TextBlock qui est censé le contenir.
            # Cette situation s'avérant assez courante, nous avons développé une manière de la contourner presque systématiquement.

            # on appelle le dictionnaire de zones des lignes et on boucle sur chaque ligne :
            for ligne_ID in dic_zones_lignes:
                # on créé des variables signalant les zones de la ligne courante :
                HPOS_L = float(dic_zones_lignes[ligne_ID]["HPOS_L"])
                VPOS_L = float(dic_zones_lignes[ligne_ID]["VPOS_L"])
                WIDTH_L = float(dic_zones_lignes[ligne_ID]["WIDTH_L"])
                HEIGHT_L = float(dic_zones_lignes[ligne_ID]["HEIGHT_L"])
                # On fait les calcules permettant de déterminer si une TextLine est contenue par un TextBlock dans la page :
                # Pour les comprendre, la documentation visuelle des régions iiif peut être utile :
                # https://iiif.io/api/image/2.1/#image-request-parameters
                if HPOS_T <= HPOS_L + 50:
                    if VPOS_T <= VPOS_L + 50:
                        if HPOS_T + WIDTH_T + 50 >= HPOS_L + WIDTH_L:
                            if VPOS_T + HEIGHT_T + 50 >= VPOS_L + HEIGHT_L:
                                # variable signalant la ligne courante :
                                contenu = Alto.xpath("//alto:TextLine[@ID='{}']".format(ligne_ID), namespaces=NS)[0]
                                # on l'ajoute au TextBlock courant :
                                TextBlock.append(contenu)
                                # et puisque on écrit une ligne dont l'ID existe déjà... l'ancienne disparaît automatiquement sur le fichier ALTO ! ;)
                                TextLines_corriges += 1

                # L'ajout de "60" points permet de rendre le calcul plus souple et de prendre en compte une marge d'erreur dans la construction des régions.
                # Cette marge d'erreur correspond à la hauteur moyenne d'une ligne sur l'image.
                # En effet, il est usuel que les régions des lignes dépassent les TextBlock qui les contiennent.
                # Cela arrive quand les entrées sont serrées : eScriptorium établit automatiquement les zones de la ligne tracée par l'utilisateur, qui ne peut controler ce dépassement
                # Ce sont ainsi presque exclusivement les premières ou dernières lignes d'une entrée qui sont susceptible de ne pas rentrer dans le calcul.
                # Le script prend en compte les lignes exclues et les signale, mais cette marge supplémentaire permet d'éviter préalablement la très grande majorité des problèmes.
                # Cette marge est statistiquement adaptée aux documents traités par le codeur, il sera peut-être nécessaire de l'adapter à d'autres corpus ou qualités d'images.

        # on calcule combien de TextBlock vides ont été alimentés avec des lignes :
        TextBlocks_vides_restant = Alto.xpath("//alto:TextBlock[not(descendant::alto:TextLine)][not(@TAGREFS='{}')]".format(MainZone), namespaces=NS)
        TextBlocks_corriges = len(TextBlocks_vides) - len(TextBlocks_vides_restant)
        # on affiche les résultats sur le terminal :
        if TextLines_corriges >= 1:
            print("\t   ✓ Correction automatique : {} lignes correspondant à {} zones vides ont été déplacées vers ces zones".format(TextLines_corriges, TextBlocks_corriges))
        else:
            print("\t  [!] Correction automatique : aucune ligne n'a été déplacées vers les zones [TextBlock] vides. Il est possible que ces zones vides soient des erreurs de saisie sur eScriptorium")

        # === 5. On gère les lignes qui n'ont pas été associées à aucun TextBlock autre que "MainZone" ===
        # S'il reste des lignes directement dans des Textblock "MainZone", cela peut être une erreur.
        # On les affichera dans le terminal pour que l'utilisateur puisse le déterminer.
        # C'est une erreur récurrente puisque sur l'interface eScriptorium, l'utilisateur peut dessiner des lignes qui dépassent les TextBlocks qui les contiennent.

        # on créé une variable qui indique si le TextBlock "MainZone" contient des TextLines :
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(MainZone), namespaces=NS):
            TextLine_dans_MainZone = Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(MainZone), namespaces=NS)
        else:
            TextLine_dans_MainZone = None
        # on récupère aussi le numéro de la page s'il existe ; il servira à l'utilisateur comme guide pour la correction :
        if Alto.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS):
            NumberingZone = Alto.xpath("//alto:OtherTag[@LABEL='NumberingZone']/@ID", namespaces=NS)[0]
        else:
            NumberingZone = None
        if Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(NumberingZone), namespaces=NS):
            numero_page = Alto.xpath("//alto:TextBlock[@TAGREFS='{}']/alto:TextLine//@CONTENT".format(NumberingZone), namespaces=NS)[0]
        else:
            numero_page = "inconnue"
        # s'il y a des TextLine directement dans le TextBLock "MainZone", on l'indique sur le terminal :
        if TextLine_dans_MainZone:
            print("\t  [!] ATTENTION : Les lignes suivantes ne sont associées à aucune entry/entryEnd et n'ont pas été traitées [Les TextLine se situent directement dans des TextBlock 'Mainzone']:")
            # et on signale chaque ligne susceptible de faire partie des informations à encoder :
            for TextLine in TextLine_dans_MainZone:
                TextLine = TextLine + " (page {})".format(numero_page.replace("—", "").replace(" ", ""))
                print("\t        " + TextLine)
                # on ajoute la ligne à la liste en return, qui servira à alimenter le fichier problemes.txt
                lignes_MainZone.append(TextLine)

        # === 7. On écrit le résultat dans un nouveau document ===
        # on veut créér un document uniquement si des changements ont eu lieu ; le compteur TextLines_corriges indique cela :
        if TextLines_corriges >= 1:
            # Le document "resegmentation" sera placé cote à cote avec le document "restructuration"
            chemin_resegmentation = chemin_restructuration.replace("restructuration.xml", "resegmentation.xml")
            Alto.write(chemin_resegmentation, pretty_print=True, encoding="UTF-8", xml_declaration=True)
        else:
            chemin_resegmentation = None
    else:
        chemin_resegmentation = None
        print("\t   ✓ les lignes et les zones ont été correctement saisies par l'utilisateur/utilisatrice ")
    return chemin_resegmentation, lignes_MainZone