"""
Extraction des informations contenues dans les fichiers ALTO en sortie de l'OCR
et insertion dans un fichier XML-TEI sur le modèle de l'ODD de Caroline Corbières
Author: Juliette Janes
Date: 11/06/21
"""

import re
from lxml import etree as ET

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

def get_oeuvres(text_list, titre, n_oeuvre, n_entree, n_line_oeuvre):
    """
    Fonction qui pour une liste donnée, récupère tout les items d'une entrée et les structure.
    :param texte: liste contenant le contenu textuel à structurer
    :type texte: list of str
    :param numero_item: dernier item numéroté précédemment
    :type numero_item: int
    :param numero_entree: dernière entrée numérotée précédemment
    :type numero_entree: int
    :return : list of the items
    :rtype: list of elementtree
    """

    # je créé les regex
    oeuvre = re.compile(r'^\d{1,3}')
    info_complementaire_1 = re.compile(r'^(\S[A-Z]|[A-Z])[a-z]')
    ligne_minuscule = re.compile(r'^(\([a-z]|[a-z])')

    list = []
    dict_item ={}
    dict_desc_item ={}
    # pour chaque ligne de la 1er ligne oeuvre, à la fin de l'entrée
    for n in range(n_line_oeuvre - 1, len(text_list)):
        current_line = text_list[n]
        if oeuvre.search(current_line):
            n_oeuvre += 1
            item_xml = ET.Element("item", n=str(n_oeuvre))
            list.append(item_xml)
            identifiant_item = titre+ "_e"+str(n_entree) + "_i" + str(n_oeuvre)
            item_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_item
            num_xml = ET.SubElement(item_xml, "num")
            title_xml = ET.SubElement(item_xml, "title")
            num_xml.text = str(n_oeuvre)
            dict_item[n_oeuvre] = current_line
            n_line_item = n
        elif n - 1 == n_line_item and ligne_minuscule.search(current_line):
            dict_item[n_oeuvre] = [dict_item[n_oeuvre], current_line]
        elif n_line_item < n and info_complementaire_1.search(current_line):
            dict_desc_item[n_oeuvre] = current_line
            desc_item_xml = ET.SubElement(item_xml, "desc")
        elif n_oeuvre in dict_desc_item:
            dict_desc_item[n_oeuvre] = [dict_desc_item[n_oeuvre], current_line]
        else:
            ('LIGNE NON RECONNUE: ', current_line)

    for el in list:
        num_entree = el.xpath(".//num/text()")
        num_entree_int = int("".join(num_entree))
        name_entree = el.find(".//title")
        texte_item_entry = str(dict_item[num_entree_int])
        texte_item_entry = texte_item_entry.replace("[", "")
        texte_item_entry = texte_item_entry.replace("['", "")
        texte_item_entry = texte_item_entry.replace("', '", "")
        texte_item_entry = texte_item_entry.replace("'], '", "")
        texte_item_entry = texte_item_entry.replace("']", "")
        name_entree.text = re.sub(r'^(\S\d{1,3}|\d{1,3}).', '', texte_item_entry)

    # si le dictionnaire d'informations complémentaires est rempli, on insère ses valeurs dans l'arbre xml
    for el in list:
        if el.xpath(".//desc"):
            num_entree= int("".join(el.xpath(".//num/text()")))
            desc_entree = el.find(".//desc")
            texte_item_entry = str(dict_desc_item[num_entree])
            texte_item_entry = texte_item_entry.replace("[", "")
            texte_item_entry = texte_item_entry.replace("['", "")
            texte_item_entry = texte_item_entry.replace("', '", "")
            texte_item_entry = texte_item_entry.replace("'], '", "")
            texte_item_entry = texte_item_entry.replace("']", "")
            desc_entree.text = texte_item_entry
    return list, n_oeuvre


def extInfo_CatSimple(document, title, list_xml, n_entree=0, n_oeuvre=0):
    """
    Fonction permettant, pour un catalogue dit de typologie simple, c'est-à-dire ayant des entrées
    où chaque ligne correspond à une information précise, d'extraire les différentes données contenues dans
    le fichier alto et de les insérer dans un fichier tei
    :param document: fichier alto parsé par etree
    :type document: lxml.etree._ElementTree
    :return: entrees_page
    :rtype: list of lxml.etree._ElementTree
    """

    # instanciation du namespace et de la liste finale
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    entrees_page = []
    n = 0
    dict_entries = {}
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)[0]
    # récupération du contenu textuel par entrée
    for entry in document.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree + "']", namespaces=NS):
        texte_entry = entry.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS)
        dict_entries[n] = texte_entry
        n += 1

    # instanciation des regex pour récupérer les auteurs et oeuvres (type de catalogue => Rouen 1850-1880)
    auteur = re.compile(r'^(\S|[A-Z])[A-ZÉ]{3,}')
    oeuvre = re.compile(r'^(\d{1,3}). \w')

    for num_entry in dict_entries:
        # Dans un premier temps on récupère l'emplacement de l'auteur et de la première oeuvre dans l'entrée
        text_list = dict_entries[num_entry]
        n_line = 0
        n_line_oeuvre = 0
        n_line_auteur = 0
        for ligne in text_list:
            n_line += 1
            if auteur.search(ligne):
                n_line_auteur = n_line
            elif oeuvre.search(ligne):
                if n_line_oeuvre == 0:
                    n_line_oeuvre = n_line
            else:
                pass
        if num_entry == 0 and n_line_auteur == 0:
            # il s'agit d'une entryEnd
            list_item_entryEnd, n_oeuvre = get_oeuvres(text_list, title, n_oeuvre, n_entree, n_line_oeuvre)
            entree_end = list_xml.find(".//entry[@n='"+str(n_entree)+"']")
            for item in list_item_entryEnd:
                entree_end.append(item)
        elif n_line_auteur != 0 and n_line_oeuvre != 0:
            # il s'agit d'une entry normale
            # je créé les balises xml nécessaires par la suite
            n_entree = n_entree + 1
            root_entry_xml = ET.Element("entry", n=str(n_entree))
            identifiant_entry = title + "_e" + str(n_entree)
            root_entry_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_entry
            desc_auteur_xml = ET.SubElement(root_entry_xml, "desc")
            auteur_xml = ET.SubElement(desc_auteur_xml, "name")
            trait_xml = ET.SubElement(desc_auteur_xml, "trait")
            p_trait_xml = ET.SubElement(trait_xml, "p")

            # récupération de la ligne auteur et de ou des lignes trait et intégration dans les balises xml
            n = 0
            print("AUTEUR ", n_line_auteur, "1ER OEUVRE ", n_line_oeuvre)
            liste_trait = []
            for ligne in text_list:
                n += 1
                if n == n_line_auteur:
                    # à modifier quand l'auteur et l'information biographique sont sur la même ligne
                    auteur_xml.text = ligne
                elif n < n_line_oeuvre:
                    liste_trait.append(ligne)
                trait_str = "\n".join(liste_trait)
                p_trait_xml.text = trait_str

            list_item_entry, n_oeuvre = get_oeuvres(text_list, title, n_oeuvre, n_entree, n_line_oeuvre)
            for item in list_item_entry:
                root_entry_xml.append(item)

            try:
                entrees_page.append(root_entry_xml)
            except Exception:
                print("entrée non ajoutée")
        else:
            print("Problème technique : "+ str(text_list) + str(num_entry))
    return list_xml, entrees_page, n_entree, n_oeuvre


def extInfo_CatDouble(document, title, list_xml, n_entree=0, n_oeuvre=0):
    """
    Fonction permettant, pour un catalogue dit de typologie double, c'est-à-dire ayant des entrées où les noms des arti-
    stes et les informations biographiques sont sur la même ligne, d'extraire les différentes données contenues dans
    le fichier alto et de les insérer dans un fichier tei
    :param document: fichier alto parsé par etree
    :type document: lxml.etree._ElementTree
    :return: entrees_page
    :rtype: list of lxml.etree._ElementTree
    """
    # instanciation du namespace et de la liste finale
    NS = {'alto': 'http://www.loc.gov/standards/alto/ns-v4#'}
    entrees_page = []
    n = 0
    dict_entries = {}
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)[0]
    # récupération du contenu textuel par entrée
    for entry in document.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree + "']", namespaces=NS):
        texte_entry = entry.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS)
        dict_entries[n] = texte_entry
        n += 1

    # instanciation des regex pour récupérer les auteurs et oeuvre
    auteur = re.compile(r'^(\S|[A-Z])[A-ZÉ]{3,}')
    auteur_recuperation = re.compile(r'^(\S|[A-Z])[A-ZÉ]{3,}(.*)\),')
    auteur_sans_nom = re.compile(r'((^(\S|[A-Z])[A-ZÉ]{3,})|-(.*)(,))')
    limitation_auteur_infobio = re.compile(r'(\),).*')
    oeuvre = re.compile(r'^\d{1,3}')

    for num_entry in dict_entries:
        # Dans un premier temps on récupère l'emplacement de l'auteur et de la première oeuvre dans l'entrée
        text_list = dict_entries[num_entry]
        n_line = 0
        n_line_oeuvre = 0
        n_line_auteur = 0
        for ligne in text_list:
            n_line += 1
            if auteur.search(ligne):
                n_line_auteur = n_line
            elif oeuvre.search(ligne):
                if n_line_oeuvre == 0:
                    n_line_oeuvre = n_line
            else:
                pass
        if num_entry == 0 and n_line_auteur == 0:
            # il s'agit d'une entryEnd
            list_item_entryEnd, n_oeuvre = get_oeuvres(text_list, title, n_oeuvre, n_entree, n_line_oeuvre)
            entree_end = list_xml.find(".//entry[@n='" + str(n_entree) + "']")
            for item in list_item_entryEnd:
                entree_end.append(item)
        elif n_line_auteur != 0 and n_line_oeuvre != 0:
            # il s'agit d'une entry normale
            # je créé les balises xml nécessaires par la suite
            n_entree = n_entree + 1
            root_entry_xml = ET.Element("entry", n=str(n_entree))
            identifiant_entry = title + "_e" + str(n_entree)
            root_entry_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_entry
            desc_auteur_xml = ET.SubElement(root_entry_xml, "desc")
            auteur_xml = ET.SubElement(desc_auteur_xml, "name")
            trait_xml = ET.SubElement(desc_auteur_xml, "trait")
            p_trait_xml = ET.SubElement(trait_xml, "p")

            # récupération de la ligne auteur et de ou des lignes trait et intégration dans les balises xml
            n = 0
            print("AUTEUR ", n_line_auteur, "1ER OEUVRE ", n_line_oeuvre)
            liste_trait = []
            for ligne in text_list:
                n += 1
                if n == n_line_auteur:
                    # à modifier quand l'auteur et l'information biographique sont sur la même ligne
                    auteur_texte = auteur_recuperation.search(ligne)
                    if auteur_texte == None:
                        auteur_sans_prenom = auteur_sans_nom.search(ligne)
                        auteur_xml.text = auteur_sans_prenom.group(0)
                    else:
                        auteur_xml.text = auteur_texte.group(0)
                    info_bio = limitation_auteur_infobio.search(ligne)
                    if info_bio != None:
                        liste_trait.append(info_bio.group(0).replace('),',''))

                elif n < n_line_oeuvre:
                    liste_trait.append(ligne)
                trait_str = "\n".join(liste_trait)
                p_trait_xml.text = trait_str

            list_item_entry, n_oeuvre = get_oeuvres(text_list, title, n_oeuvre, n_entree, n_line_oeuvre)
            for item in list_item_entry:
                root_entry_xml.append(item)

            try:
                entrees_page.append(root_entry_xml)
            except Exception:
                print("entrée non ajoutée")
        else:
            print("Problème technique : " + str(text_list) + str(num_entry))
    return list_xml, entrees_page, n_entree, n_oeuvre
