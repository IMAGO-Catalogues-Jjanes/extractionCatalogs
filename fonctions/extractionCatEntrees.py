"""
Extraction des informations contenues dans les fichiers ALTO en sortie de l'OCR
et insertion dans un fichier XML-TEI sur le modèle de l'ODD de Caroline Corbières
Author: Juliette Janes
Date: 11/06/21
"""

import re
from lxml import etree as ET
from fonctions.instanciation_regex import *

def nettoyer_liste_str(texte):
    """
    Fonction qui permet de nettoyer une chaîne de caractère issue d'une liste
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
    n=0
    dict_entrees_texte = {}
    tagref_entree = alto.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)[0]
    # récupération du contenu textuel par entrée
    for entree in alto.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree + "']", namespaces=NS):
        texte_entree = entree.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS)
        dict_entrees_texte[n] = texte_entree
        n += 1
    return dict_entrees_texte

def get_EntryEnd_texte(alto):
    """
    Fonction qui permet, pour un document alto, de récupérer tout son contenu textuel dans les entryEnd
    :param alto: fichier alto parsé par etree
    :type alto: lxml.etree._ElementTree
    :return: liste contenant le contenu textuel de l'entry end par ligne
    :rtype: list of str
    """
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    tagref_entree_end = alto.xpath("//alto:OtherTag[@LABEL='EntryEnd']/@ID", namespaces=NS)[0]
    # récupération du contenu textuel par entrée
    texte_entree = alto.xpath("//alto:TextBlock[@TAGREFS='"+tagref_entree_end+"']//alto:String/@CONTENT", namespaces=NS)
    return texte_entree

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
    for ligne in entree_texte:
        n_line += 1
        if auteur_regex.search(ligne):
            n_line_auteur = n_line
        elif oeuvre_regex.search(ligne):
                n_line_oeuvre.append(n_line)
        else:
            pass
    return n_line_auteur, n_line_oeuvre

def create_entry_xml(document, title, n_entree, infos_biographiques=0):
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
    corresp_page= document.xpath("//alto:fileIdentifier/text()", namespaces=NS)
    if corresp_page != []:
        entree_xml.attrib["source"] = corresp_page[0]
    else:
        entree_xml.attrib["source"] = document.xpath("//alto:fileName/text()", namespaces=NS)[0]
    desc_auteur_xml = ET.SubElement(entree_xml, "desc")
    auteur_xml = ET.SubElement(desc_auteur_xml, "name")
    p_trait_xml = None
    if infos_biographiques == 0:
        trait_xml = ET.SubElement(desc_auteur_xml, "trait")
        p_trait_xml = ET.SubElement(trait_xml, "p")
    else:
        pass
    return entree_xml, auteur_xml, p_trait_xml


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
    print(texte_items_liste, len(texte_items_liste))
    # pour chaque ligne de la 1er ligne oeuvre, à la fin de l'entrée
    for n in range(n_line_oeuvre - 1, len(texte_items_liste)):
        current_line = texte_items_liste[n]
        if oeuvre_regex.search(current_line):
            n_oeuvre =numero_regex.search(current_line).group(0)
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



def extInfo_Cat(document, typeCat, title, list_xml, n_entree=0, n_oeuvre=0):
    """
    Fonction qui permet, pour un catalogue, d'extraire les différentes données contenues dans le fichier alto et de les
    insérer dans un fichier tei
    :param document: fichier alto parsé par etree
    :type document: lxml.etree._ElementTree
    :param typeCat: type de Catalogue (Nulle: sans information biographique, Simple: avec une information biographique
    sur la ligne en dessous du nom de l'artiste, Double: sur la même ligne que l'auteur)
    :param title: nom du catalogue à encoder
    :type title:str
    :param list_xml: ElementTree contenant la balise tei list et les potentielles précédentes entrées encodées
    :type list_xml: lxml.etree._ElementTree
    :param n_oeuvre: numéro employé pour l'oeuvre précédente
    :type n_oeuvre: int
    :param n_entree: numéro employé pour l'entrée précédente
    :type n_entree: int
    :return: entrees_page
    :rtype: list of lxml.etree._ElementTree
    """

    list_entrees_page = []
    dict_entrees_texte = get_texte_alto(document)
    list_entree_end_texte = get_EntryEnd_texte(document)
    if list_entree_end_texte != []:
        # il s'agit d'une entryEnd
        n_line_auteur, n_line_oeuvre = get_structure_entree(list_entree_end_texte, auteur_regex, oeuvre_regex)
        try:
            list_item_entryEnd_xml, n_oeuvre = get_oeuvres(list_entree_end_texte, title, n_oeuvre, n_entree,
                                                           n_line_oeuvre[0])
            entree_end_xml = list_xml.find(".//entry[@n='" + str(n_entree) + "']")
            for item in list_item_entryEnd_xml:
                entree_end_xml.append(item)
        except Exception:
            a_ecrire = "\n" + str(n_entree) + " " + str(list_entree_end_texte)
            with open("pb_techniques.txt", mode="a") as f:
                f.write(a_ecrire)
    for num_entree in dict_entrees_texte:
        # Dans un premier temps on récupère l'emplacement de l'auteur et de la première oeuvre dans l'entrée
        entree_texte = dict_entrees_texte[num_entree]
        n_line_auteur, n_line_oeuvre = get_structure_entree(entree_texte, auteur_regex, oeuvre_regex)
        # en commentaire, les lignes condition à activer lorsque l'on s'occupe d'un catalogue entièrement numérisé
        # à la main
        # if num_entree == 0 and n_line_auteur == 0:
        # il s'agit d'une entry normale
        # je créé les balises xml nécessaires par la suite
        n_entree = n_entree + 1
        if typeCat == "Nulle":
            entree_xml, auteur_xml, p_trait_xml = create_entry_xml(document, title, n_entree, infos_biographiques=1)
        else:
            entree_xml, auteur_xml, p_trait_xml = create_entry_xml(document, title, n_entree)
        n = 0
        print("AUTEUR ", n_line_auteur, "OEUVRES", n_line_oeuvre)
        if typeCat == "Nulle":
            auteur_xml.text = entree_texte[n_line_auteur]
        elif typeCat == "Simple":
            liste_trait_texte = []
            for ligne in entree_texte:
                n += 1
                if n == 1:
                    auteur_xml.text = ligne
                elif n < n_line_oeuvre[0]:
                    liste_trait_texte.append(ligne)
            p_trait_xml.text = "\n".join(liste_trait_texte)
        elif typeCat == "Double" or typeCat == "Triple":
            liste_trait_texte = []
            for ligne in entree_texte:
                n += 1
                if n == 1:
                    auteur_texte = auteur_recuperation_regex.search(ligne)
                    if auteur_texte != None:
                        auteur_xml.text = auteur_texte.group(0)
                    elif auteur_sans_prenom_regex.search(ligne) != None:
                        auteur_xml.text = auteur_sans_prenom_regex.search(ligne).group(0)
                    info_bio = limitation_auteur_infobio_regex.search(ligne)
                    if info_bio != None:
                        liste_trait_texte.append(info_bio.group(0).replace('),', ''))

                elif n < n_line_oeuvre[0]:
                    liste_trait_texte.append(ligne)
                p_trait_xml.text = "\n".join(liste_trait_texte)

        try:
            list_item_entree, n_oeuvre = get_oeuvres(entree_texte, typeCat, title, n_oeuvre, n_entree, n_line_oeuvre[0])
            for item in list_item_entree:
                entree_xml.append(item)
        except Exception:
            output_txt = "\n" + str(n_entree) + " ".join(entree_texte)
            with open("pb_techniques.txt", mode="a") as f:
                f.write(output_txt)
        try:
            list_entrees_page.append(entree_xml)
        except Exception:
            print("entrée non ajoutée")

    return list_xml, list_entrees_page, n_entree, n_oeuvre
