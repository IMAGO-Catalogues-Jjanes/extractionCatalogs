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
    texte = texte.replace("[", "")
    texte = texte.replace("['", "")
    texte = texte.replace("', '", "")
    texte = texte.replace("'], '", "")
    texte = texte.replace("']", "")
    return texte


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
              "\t\tVous pouvez changer manuellement, dans le fichier ALTO original, le nom du type de zone correspondant (balise <OtherTag LABEL=''>)\n"
              "\t\tPour plus d'informations : https://github.com/SegmOnto\n")

    # dictionnaire et variable utilisées pour récupérer le texte :
    dict_entrees_texte = {}
    n = 0
    # liste des ID TextBlock, qui sera utilisée après pour récupérer les régions de l'image indiquées au même niveau :
    iiif_regions = []
    # Si les entrées sont conformes à Segmonto :
    if tagref_entree != None:
        # récupération du contenu de chaque entrée, si elle contient du texte
        # (cela permet de ne pas générer des entrées vides qui nuisent à la conformité et aux numérotations de l'output TEI)
        for entree in alto.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree + "']", namespaces=NS):
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
    Fonction qui permet, pour un document alto, de récupérer tout son contenu textuel dans les entryEnd
    :param alto: fichier alto parsé par etree
    :type alto: lxml.etree._ElementTree
    :return: liste contenant le contenu textuel de l'entry end par ligne
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
        # notons qu'une page ALTO ne peut avoir qu'un entryEnd, nous n'avons donc pas besoin de boucler la liste
        return list_entree_end_texte


def get_structure_entree(entree_texte, auteur_regex, oeuvre_regex):
    """
    Fonction qui, pour une entrée, récupère la ligne contenant son auteur et sa première oeuvre
    :param entree_texte: liste contenant toutes les lignes d'une entrée
    :type entree_texte: list of str
    :param auteur_regex: regex permettant de déterminer qu'une line commençant par plusieurs lettres majuscules est
    possiblement une ligne contenant le nom de l'artiste
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
    n_line_oeuvre = []
    n_line_auteur = 0
    # si entree_texte n'est pas None (d'ailleurs objet None n'est pas itérable)
    if entree_texte:
        for ligne in entree_texte:
            n_line += 1
            if auteur_regex.search(ligne):
                n_line_auteur = n_line
            elif oeuvre_regex.search(ligne):
                n_line_oeuvre.append(n_line)
            else:
                pass
    return n_line_auteur, n_line_oeuvre


def get_oeuvres(texte_items_liste, typeCat, titre, id_n_oeuvre, id_n_entree, n_line_oeuvre=1):
    """
    Fonction qui pour une liste donnée, récupère tout les items (oeuvre) d'une entrée et les structure.
    :param texte_items_liste: liste de chaîne de caractères où chaque chaîne correspond à une ligne et la liste correspond
    à l'entrée
    :type texte: list of str
    :param typeCat: type du catalogue à encoder
    :type typeCat: str
    :param titre: nom du catalogue à encoder
    :type titre: str
    :param id_n_oeuvre: numéro employé pour l'oeuvre précédente
    :type id_n_oeuvre: int
    :param id_n_entree: numéro employé pour l'entrée précédente
    :type id_n_entree: int
    :param n_line_oeuvre: liste de numéro indiquant la ligne de chaque oeuvre
    :type n_line_oeuvre:list of int
    :return texte_items_liste: liste des oeuvres chacune encodée en tei
    :rtype texte_items_liste: list of elementtree
    :return id_n_oeuvre: numéro employé pour la dernière oeuvre encodée dans la fonction
    :rtype id_n_oeuvre: int
    """
    list_item_ElementTree = []
    dict_item_texte = {}
    dict_item_desc_texte = {}
    print("\t\t  ", texte_items_liste, len(texte_items_liste))
    # pour chaque ligne de la 1er ligne oeuvre, à la fin de l'entrée
    for n in range(n_line_oeuvre - 1, len(texte_items_liste)):
        current_line = texte_items_liste[n]
        if oeuvre_regex.search(current_line):
            n_oeuvre = numero_regex.search(current_line).group(0)
            item_xml = ET.Element("item", n=str(n_oeuvre))
            list_item_ElementTree.append(item_xml)
            identifiant_item = titre + "_e" + str(id_n_entree) + "_i" + str(n_oeuvre)
            item_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_item
            num_xml = ET.SubElement(item_xml, "num")
            title_xml = ET.SubElement(item_xml, "title")
            num_xml.text = n_oeuvre
            dict_item_texte[n_oeuvre] = current_line
            n_line_item = n
        elif n - 1 == n_line_item and ligne_minuscule_regex.search(current_line):
            dict_item_texte[n_oeuvre] = [dict_item_texte[n_oeuvre], current_line]
            n_line_item = n
        elif n - 1 == n_line_item and info_complementaire_regex.search(current_line):
            dict_item_desc_texte[n_oeuvre] = current_line
        elif n_oeuvre in dict_item_desc_texte:
            print(n_oeuvre)
            dict_item_desc_texte[n_oeuvre] = [dict_item_desc_texte[n_oeuvre], current_line]
        else:
            ('LIGNE NON RECONNUE: ', current_line)
    for el in list_item_ElementTree:
        num_item = "".join(el.xpath("@n"))
        name_item = el.find(".//title")
        texte_name_item = str(dict_item_texte[num_item])
        texte_name_item_propre = nettoyer_liste_str(texte_name_item)
        if el.xpath(".//desc"):
            desc_item = el.find(".//desc")
            texte_desc_item = str(dict_item_desc_texte[num_item])
            desc_item.text = nettoyer_liste_str(texte_desc_item)
        if typeCat == "Triple" and info_comp_tiret_regex.search(texte_name_item_propre):
            desc_el_xml = ET.SubElement(el, "desc")
            desc_tiret = info_comp_tiret_regex.search(texte_name_item_propre).group(0)
            desc_el_xml.text = desc_tiret
            texte_name_item_propre = re.sub(r'— .*', '', texte_name_item_propre)
        name_item.text = re.sub(r'^(\S\d{1,3}|\d{1,3}).', '', texte_name_item_propre)

    return list_item_ElementTree, id_n_oeuvre


def create_entry_xml(document, title, n_entree, iiif_region, infos_biographiques=0):
    """
    Fonction qui permet de créer toutes les balises TEI nécessaires pour encoder une entrée
    :param title: nom du catalogue
    :type title: str
    :param n_entree: numéro de l'entrée
    :type n_entree: str
    :param infos_biographiques: Existence (ou non) d'une partie information biographique sur l'artiste dans les entrées
    du catalogue (par défaut elle existe)
    :type infos_biographiques:int
    :return: balises vides pour l'encodage d'une entrée
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    entree_xml = ET.Element("entry", n=str(n_entree))
    identifiant_entree = title + "_e" + str(n_entree)
    entree_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_entree
    corresp_page = document.xpath("//alto:fileIdentifier/text()", namespaces=NS)
    if corresp_page != []:
        entree_xml.attrib["source"] = corresp_page[0]

        if entree_xml.attrib["source"].__contains__("/full/full/0/default."):
            # TODO chaque entrée prend toujours la premiere coupe de la feuille...
            n = 0
            x = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@HPOS"), namespaces=NS)
            y = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@VPOS"), namespaces=NS)
            w = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@WIDTH"), namespaces=NS)
            h = document.xpath("//alto:TextBlock[@ID='{}']/{}".format(iiif_region, "@HEIGHT"), namespaces=NS)
            coupe = str(x) + "," + str(y) + "," + str(w) + "," + str(h)
            coupe = coupe.replace("'", "").replace("[", "").replace("]", "")

            lien_iiif = entree_xml.attrib["source"].replace("/full/full/0/default.",
                                                            "/{region}/{size}/{rotation}/{quality}.").format(
                region=coupe,
                size="full",
                rotation="0",
                quality="default"
            )
            entree_xml.attrib["source"] = lien_iiif
            n += 1
    else:
        entree_xml.attrib["source"] = document.xpath("//alto:fileName/text()", namespaces=NS)[0]
        # il n'y aura pas de référence iiif, mais la variable doit être référencée :
        lien_iiif = ""
    desc_auteur_xml = ET.SubElement(entree_xml, "desc")
    auteur_xml = ET.SubElement(desc_auteur_xml, "name")
    p_trait_xml = None
    if infos_biographiques == 0:
        trait_xml = ET.SubElement(desc_auteur_xml, "trait")
        p_trait_xml = ET.SubElement(trait_xml, "p")
    else:
        pass
    return entree_xml, auteur_xml, p_trait_xml, lien_iiif