"""
Fonctions secondaires pour extractionCatEntrees.py
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

from lxml import etree as ET
from extractionCatalogs.variables.instanciation_regex import *


def nettoyer_liste_str(texte):
    """
    Fonction pour nettoyer une chaîne de caractères qui était auparavant une liste
    :param texte: ancienne liste de listes (parfois de listes) transformée en chaîne de caractères
    :type texte: str
    :return: chaîne de caractères nettoyée
    :rtype: str
    """
    texte = texte.replace("'], '", "")
    texte = texte.replace("['", "")
    texte = texte.replace('["', '')
    texte = texte.replace("']", "")
    texte = texte.replace("]", "")
    texte = texte.replace("[", "")
    texte = texte.replace("{", "")
    texte = texte.replace("}", "")
    texte = texte.replace('", ', '')
    return texte


def nettoyer_liste_str_problemes(texte):
    """
    Fonction pour nettoyer une chaîne de caractères qui était auparavant une liste
    :param texte: ancienne liste de listes (parfois de listes) transformée en chaîne de caractères
    :type texte: str
    :return: chaîne de caractères nettoyée
    :rtype: str
    """
    texte = texte.replace(')]"', ')')
    texte = texte.replace(")]'", ")")
    texte = texte.replace("['[", "")
    texte = texte.replace('["[', "")
    texte = texte.replace("]", "")
    texte = texte.replace("[", "")
    texte = texte.replace("\\'", "'")
    return texte


def ordonner_altos(liste_en_desordre):
    """
    Ordonne la liste des fichiers en input. Cette fonction permet que la numérotation dans les noms des fichiers en
    input aient ou n'aient pas de "zéros non significatifs" (ex: "9" ou "09"). La liste est ordonnée par nombre de
    caractères dans le nom, puis alpha-numériquement. En effet, une variation dans le nombre de caractères implique deux
    possibilités : soit l'absence de "zéros non significatifs", soit l'appartenance à un ensemble différent de documents
    ALTO.
    :param liste_en_desordre: liste des fichiers obtenus avec os.listdir()
    :type liste_en_desordre: list
    :return: liste_en_ordre
    :rtype: lsit
    """
    # on créé un dictionnaire qui contiendra autant de clés que de longueurs de chaînes de caractères constituant les
    # noms des fichiers :
    dic_lists = {}
    for item in liste_en_desordre:
        # si un clé correspondant à la longueur de la chaîne existe déjà :
        if len(item) in dic_lists.keys():
            # sa valeur est une liste et on y ajoute la chaîne :
            dic_lists[len(item)].append(item)
        else:
            # ou bien on créé cette liste, puis on ajoute la chaîne :
            dic_lists[len(item)] = []
            dic_lists[len(item)].append(item)
    # on ordonne les items du dictionnaire par ordre croissant (en les mettant en ordre dans un nouveau dictionnaire) :
    dic_lists_ordered = dict(sorted(dic_lists.items()))
    for key in dic_lists_ordered:
        # on met en ordre chaque liste constituant notre dictionnaire :
        ordered_list = sorted(dic_lists[key])
        dic_lists_ordered[key] = ordered_list

    # on créé une seule liste de noms de fichiers en concaténant les listes qui constituent le dictionnaire :
    liste_en_ordre = []
    for list in dic_lists_ordered:
        liste_en_ordre += dic_lists_ordered[list]
    return liste_en_ordre

def get_texte_alto(alto):
    """
    Fonction qui permet, pour un document alto, de récupérer tout son contenu textuel dans les entrées
    :param alto: fichier alto parsé par etree
    :type alto: lxml.etree._ElementTree
    :return: dictionnaire ayant comme clé le numéro de l'entrée et comme valeur tout son contenu textuel
    :rtype: dict{int:list of str}
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}

    # On vérifie que la dénomination des entrées est conforme à l'ontologie Segmonto ('CustomZone')
    if alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']", namespaces=NS):
        # Si c'est le cas, on créé une variable qui récupère l'ID faisant référence aux régions de type 'CustomZone' :
        tagref_entree = alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entry']/@ID", namespaces=NS)[0]
    else:
        # Si non, la valeur de la variable sera None puis écartée, et on affiche un avertissement :
        tagref_entree = None
        print("\n\tATTENTION : Ce fichier ALTO a été restructuré, mais il n'est pas conforme à l'ontologie Segmonto.\n"
              "\t\tLes entrées doivent être indiquées comme des 'CustomZone:entry' lors de la segmentation.\n"
              "\t\tVous pouvez changer manuellement dans les fichier ALTO le nom du type de zone correspondant (balise <OtherTag LABEL=''>)\n"
              "\t\tPour plus d'informations : https://github.com/SegmOnto\n")

    # dictionnaire et variable utilisées pour récupérer le texte :
    dict_entrees_texte = {}
    n = 0
    # liste des ID TextBlock, qui sera utilisée après pour récupérer les régions de l'image indiquées au même niveau :
    iiif_regions = []
    # Si les entrées sont conformes à Segmonto :
    if tagref_entree != None:
        # Pour chaque entrée dans le document :
        for entree in alto.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree + "']", namespaces=NS):
            # Si l'entrée contient du texte :
            # (cela permet de ne pas générer des entrées vides, issues d'erreurs de saisie sur eScriptorium, qui nuisent à la conformité et aux numérotations de l'output TEI)
            if entree.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS):
                # on asigne le texte à une variable :
                texte_entree = entree.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS)
                # on utilise cette variable pour creer un item dans un dictionnaire d'entrées :
                dict_entrees_texte[n] = texte_entree
                # on ajoute aussi l'ID du TextBlock a iiif_regions, qui nous servira à récupérer des informations sur le cadre de l'image
                iiif_regions += entree.xpath("@ID", namespaces=NS)
                # on augmente l'index n, pour que la clé du dictionnaire change à l'itération suivante :
                n += 1
    return dict_entrees_texte, iiif_regions


def get_EntryEnd_texte(alto):
    """
    Récupère le contenu textuel des entryEnd d'un fichier ALTO
    :param alto: fichier alto parsé par etree
    :type alto: lxml.etree._ElementTree
    :return: liste contenant le contenu textuel de l'entryEnd par ligne
    :rtype: list of str
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    # on vérifie que la zone entryEnd a été référencée dans une balise <OtherTag> du fichier :
    # (ça peut ne pas être le cas pour des catalogues sans ce type d'entrée ; dans ces cas, le script ne pourrait pas
    # tourner sans cette condition)
    if alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']", namespaces=NS):
        tagref_entree_end = alto.xpath("//alto:OtherTag[@LABEL='CustomZone:entryEnd']/@ID", namespaces=NS)[0]
        # récupération du contenu textuel par entrée
        list_entree_end_texte = alto.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree_end + "']//alto:String/@CONTENT",
                                  namespaces=NS)
        # notons qu'une page ALTO ne peut avoir qu'un entryEnd
        return list_entree_end_texte


def get_structure_entree(entree_texte, auteur_regex, oeuvre_regex, oeuvre_regex_precise):
    """
    Fonction qui, pour une liste contenant les lignes d'une entrée, récupère la ligne contenant son auteur
    et une liste des lignes contenant des oeuvres
    :param entree_texte: liste contenant toutes les lignes d'une entrée
    :type entree_texte: list of str
    :param auteur_regex: regex permettant de déterminer qu'une line commençant par plusieurs lettres majuscules est
    possiblement une ligne contenant le nom de l'auteur
    :type auteur_regex: regex
    :param oeuvre_regex: regex permettant de déterminer qu'une line commençant par plusieurs chiffres est
    possiblement une ligne contenant une oeuvre
    :type oeuvre_regex: regex
    :return n_line_auteur: numéro de la ligne contenant le nom de l'auteur
    :rtype n_line_auteur: int
    :return n_line_oeuvre: liste de numéro contenant toutes les lignes des oeuvres
    :rtype n_line_oeuvre: list of int
    """
    n_line = 0
    n_line_simplifiee = 0
    n_line_oeuvre = []
    n_line_auteur = 0
    # si entree_texte n'est pas None (un objet None n'est pas itérable)
    if entree_texte:
        # pour chaque chaine de la liste :
        for ligne in entree_texte:
            n_line += 1
            # Si la regex auteur correspond à la ligne courante :
            if auteur_regex.search(ligne):
                # la valeur de n_ligne devient la ligne courante :
                n_line_auteur = n_line
            # si une regex précise a été choisie pour les oeuvres et qu'elle correspond à la ligne courante :
            elif oeuvre_recuperation_regex.search(ligne):
                n_line_oeuvre.append(n_line)
            else:
                # les lignes d'informations biographiques ne seront pas traitées
                pass
        # Si la liste relative aux oeuvres est vide, on utilise une regex moins rigoureuse susceptible de ne pas différencier des adresses :
        regex_adresse = re.compile(r'^[*]*\d{1,4},')
        if not n_line_oeuvre:
            for ligne in entree_texte:
                n_line_simplifiee += 1
                if regex_adresse.search(ligne):
                    pass
                elif oeuvre_regex.search(ligne):
                    n_line_oeuvre.append(n_line_simplifiee)
        return n_line_auteur, n_line_oeuvre


def get_oeuvres(entree_texte, titre, n_oeuvre, n_entree, n_line_oeuvre=1):
    """
    Fonction qui pour une liste donnée, récupère tout les items (oeuvre) d'une entrée et les structure.
    :param entree_texte: liste de chaîne de caractères où chaque chaîne correspond à une ligne et la liste correspond
    à l'entrée
    :type entree_texte: list of str
    :param titre: nom du catalogue à encoder
    :type titre: str
    :param n_oeuvre: numéro employé pour l'oeuvre précédente
    :type n_oeuvre: int
    :param n_entree: numéro employé pour l'entrée précédente
    :type n_entree: int
    :param n_line_oeuvre: premiere ligne oeuvre indiquée dans une liste d'oeuvres
    :type n_line_oeuvre:list of int
    :return list_item_ElementTree: liste des oeuvres chacune encodée en tei
    :rtype list_item_ElementTree: list of elementtree
    :return n_oeuvre: numéro employé pour la dernière oeuvre encodée dans la fonction
    :rtype n_oeuvre: int
    """
    # on établie la liste d'objets etree "item" qu'on aura en return :
    list_item_ElementTree = []
    # dictionnaire pour les oeuvres :
    dict_item_texte = {}
    dict_item_texte_multiligne = {}
    # dictionnaire pour les description éventuelles des oeuvres :
    dict_item_desc_texte = {}
    # liste de numéros d'items pour détecter des répétition (item bis):
    list_item_numero = []
    # liste d'oeuvres à récupérer pour afficher sur le terminal :
    liste_oeuvres_terminal = []
    # range renvoie une séquence de numéros, qui équivaut aux index d'une liste. Ici, on obtient une liste des
    # lignes entre la première oeuvre et la dernière :
    lignes_oeuvres = range(n_line_oeuvre - 1, len(entree_texte))
    # on boucle sur chaque ligne oeuvre :
    for n in lignes_oeuvres:
        # on sélectionne la ligne référée par le numéro courant dans la liste :
        current_line = entree_texte[n]
        # si la chaîne correspond à notre regex oeuvre basique (détécte simplement des chiffres en début de ligne) :
        if oeuvre_regex.search(current_line):
            # on extrait le numéro de l'oeuvre avec la regex correspondante :
            n_oeuvre_courante = numero_regex.search(current_line).group(0)
            # si le numéro est déjà dans la liste, on a à faire à un item bis, et on va l'ajouter à l'item antérieur
            if n_oeuvre_courante in list_item_numero:
                # on créé une deuxième balise title pour cet item bis
                title_xml = ET.SubElement(item_xml, "title")
                title_xml.text = current_line
                # on met le texte dans un chaîne, on l'utilisera après pour le faire apparaître dans le terminal
                item_bis = current_line
            # Si le numéro n'existe pas déjà (item non bis), on créé l'entrée :
            else:
                # la valeur de la variable item_bis sera None pour la mettre facilement de côté le moment venu :
                item_bis = None
                # noter que l'élément le numéro avec des items bis ne sera pas en doublon dans la liste
                list_item_numero.append(n_oeuvre_courante)
                # on crée un élément "item" avec pour attribut le numéro de l'oeuvre :
                item_xml = ET.Element("item", n=str(n_oeuvre_courante))
                # on ajoute cet objet à la liste d'items :
                list_item_ElementTree.append(item_xml)
                # on crée un identifiant pour l'item (titre du catalogue, numéro d'entrée, numéro d'item) :
                identifiant_item = titre + "_e" + str(n_entree) + "_i" + str(n_oeuvre_courante)
                # on ajoute cet identifiant comme attribut de l'item
                item_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_item
                # on créé un élément pour insérer le numéro de l'oeuvre :
                num_xml = ET.SubElement(item_xml, "num")
                # on créé un élément pour insérer le titre de l'oeuvre :
                title_xml = ET.SubElement(item_xml, "title")
                num_xml.text = n_oeuvre_courante
                # on ajoute au dictionnaire une entrée avec le numéro comme clé et la ligne entière comme valeur :
                # (nous avons créé les balises item, mais pas encore ajouté le texte, cela sera fait postérieurement)
                dict_item_texte[n_oeuvre_courante] = current_line
        # si la regex oeuvre ne marche pas on vérifie si la ligne courante ne commence pas par des chiffres
        # (Dans ce cas c'est nécessairement une deuxième ligne )
        if ligne_secondaire_regex.search(current_line):
            # on ajoute à la chaîne de caractères la deuxième ligne de l'item :
            # (la valeur de n_oeuvre_courante est celle de la ligne antérieure dès lors qu'on a sauté l'étape antérieure)
            dict_item_texte[n_oeuvre_courante] = dict_item_texte[n_oeuvre_courante] + " " + current_line
        # ou bien on vérifie si l'information est à mettre à part en tant que description avec un deuxième dictionnaire :
        #TODO : pas satisfaisant : pas de différence claire entre deuxième ligne et info complémentaire
        """
               elif info_complementaire_regex.search(current_line):
            if not dict_item_desc_texte[n_oeuvre_courante]:
                dict_item_desc_texte[n_oeuvre_courante] = current_line
            else:
                dict_item_desc_texte[n_oeuvre_courante] = dict_item_desc_texte[n_oeuvre] + " " + current_line
        else:
            ('LIGNE NON RECONNUE: ', current_line)
        """
    # pour chaque élément dans la liste d'objets "item_xml"
    for el in list_item_ElementTree:
        # on récupère le numéro de l'oeuvre :
        num_item = "".join(el.xpath("@n"))
        # on récupère la balise titre, on la remplira plus tard :
        name_item = el.find(".//title")
        # avec ce numéro, on récupère le nom de l'oeuvre dans le dictionnaire d'oeuvres puis on le nettoie :
        texte_name_item = str(dict_item_texte[num_item])
        # on nettoie la chaîne :
        texte_name_item_propre = nettoyer_liste_str(texte_name_item)
        # on ajoute l'oeuvre à la liste qui servira à l'afficher sur le terminal (avant la commande suivante afin de garder les numéros !):
        liste_oeuvres_terminal.append(texte_name_item_propre)
        # on ajoute l'eventuel item bis précédement extrait, afin qu'il apparaisse après la première apparition du numéro
        if item_bis:
            liste_oeuvres_terminal.append(item_bis)
        # on enlève les numéros et autres signes propre à l'item :
        texte_name_item_propre = re.sub(r'^(\S\d{1,3}|\d{1,3})[.]*[ ]*[—]*[ ]*', '', texte_name_item_propre)
        # si l'item a déjà des balises de description :
        # TODO : ce if est susceptible de mettre de coté des "lignes secondaires" qui seront traitées comme des "informations complémentaires"
        #  mais il faudrait que l'item ait en même temps les deux, ce qui est très exceptionnel
        if el.xpath(".//desc"):
            # on récupère la balise "description" :
            desc_item = el.find(".//desc")
            # une deuxième ligne de description ne commencera pas par "–" ou "(" ; on cherche donc une minuscule ou une majuscule :
            desc_tiret_parenthese = ligne_secondaire_regex.search(texte_name_item_propre).group(0)
            # on ajoute la ligne à la balise description :
            desc_item.text = desc_item.text + " " + desc_tiret_parenthese
        # on vérifie s'il y a des tirets/parenthèses ailleurs qu'au début, ou des points avant la fin de l'item, pour repérer des informations complémentaires :
        if info_comp_tiret_parenthese_regex.search(texte_name_item_propre):
            desc_el_xml = ET.SubElement(el, "desc")
            desc_tiret_parenthese = info_comp_tiret_parenthese_regex.search(texte_name_item_propre).group(0)
            # on enlève les tirets ou points qui nous avaient permis de localiser la chaîne :
            desc_tiret_parenthese = re.sub(r'—[ ]*|[a-z]\. ', '', desc_tiret_parenthese)
            desc_el_xml.text = desc_tiret_parenthese
            # on enlève tout ce qui vient après le tiret ou la parenthèse pour garder le titre de l'oeuvre :
            texte_name_item_propre = re.sub(r'[ ]*—[ ]*.*|[ ]*\(.*', '', texte_name_item_propre)

        # On met enfin le titre dans la balise title
        name_item.text = texte_name_item_propre
    return list_item_ElementTree, n_oeuvre, texte_name_item_propre, liste_oeuvres_terminal


def create_entry_xml(document, title, n_entree, iiif_region):
    """
    Fonction qui permet de créer toutes les balises TEI nécessaires pour encoder une entrée
    :param document: ALTO restructuré parsé
    :type document: XML object
    :param title: nom du catalogue
    :type title: str
    :param n_entree: numéro de l'entrée
    :type n_entree: int
    :param infos_biographiques: Existence (ou pas) d'une partie information biographique sur l'artiste dans les entrées
    du catalogue (par défaut elle existe)
    :type infos_biographiques: bool
    :return: balises vides pour l'encodage d'une entrée
    """
    # === 1. On créé la balise entrée et le lien iiif qui lui sera associé ===
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    entree_xml = ET.Element("entry", n=str(n_entree))
    identifiant_entree = title + "_e" + str(n_entree)
    entree_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_entree

    # on récupère le lien ou le chemin vers l'image de la page, qui sera souvent un lien iiif :
    image = document.xpath("//alto:fileIdentifier/text()", namespaces=NS)
    # s'il y en a un, on le met comme valeur de l'attribut "source" :
    if image != []:
        entree_xml.attrib["source"] = image[0]
        # on vérifie s'il s'agit d'un lien iiif en testant sa conformité :
        if entree_xml.attrib["source"].__contains__("/full/full/0/default."):
            # si c'est le cas, on récupère la découpe des entrées grâce aux ID contenus dans la variable iiif_region :
            x = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@HPOS"), namespaces=NS)
            y = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@VPOS"), namespaces=NS)
            w = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@WIDTH"), namespaces=NS)
            h = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@HEIGHT"), namespaces=NS)
            # on créé une chaîne avec ces données sur les régions :
            decoupe = str(x) + "," + str(y) + "," + str(w) + "," + str(h)
            # on nettoie la chaîne, qui provient de listes :
            decoupe = decoupe.replace("'", "").replace("[", "").replace("]", "")
            # on créée un lien iiif vers un découpage adapté pour chaque entrée :
            lien_iiif = entree_xml.attrib["source"].replace("/full/full/0/default.",
                                                            "/{region}/{size}/{rotation}/{quality}.").format(
                region=decoupe,
                size="full",
                rotation="0",
                quality="default"
            )
            # on insère ce nouveau lien dans l'attribut "source"
            entree_xml.attrib["source"] = lien_iiif
    else:
        # s'il n'y a pas de lien vers une image, on donne à la balise source la valeur de filename
        entree_xml.attrib["source"] = document.xpath("//alto:fileName/text()", namespaces=NS)[0]
        # dans ce cas il n'y aura pas de référence iiif, mais la variable doit exister car elle est en return  :
        lien_iiif = ""

    # === 2. On créé les autres balises de l'entrée ===
    # on créé la balise fille de entry :
    desc_auteur_xml = ET.SubElement(entree_xml, "desc")
    # on créé la balise nom de l'auteur :
    auteur_xml = ET.SubElement(desc_auteur_xml, "name")
    return entree_xml, desc_auteur_xml, auteur_xml, lien_iiif