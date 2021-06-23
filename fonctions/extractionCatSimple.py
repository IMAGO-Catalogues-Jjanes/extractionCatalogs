"""
Extraction des informations contenues dans les fichiers ALTO en sortie de l'OCR
et insertion dans un fichier XML-TEI sur le modèle de l'ODD de Caroline Corbières
Author: Juliette Janes
Date: 11/06/21
"""


import re
from lxml import etree as ET

def extInfo_CatSimple(document, title, list_xml = 0, n_entree=0, n_oeuvre=0):
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
    n=0
    dict_entries = {}
    tagref_entree = document.xpath("//alto:OtherTag[@LABEL='Entry']/@ID", namespaces=NS)
    # récupération du contenu textuel par entrée
    for entry in document.xpath("//alto:TextBlock[@TAGREFS='" + tagref_entree[0] + "']", namespaces=NS):
        n+=1
        texte_entry = entry.xpath("alto:TextLine/alto:String/@CONTENT", namespaces=NS)
        dict_entries[n] = texte_entry

    # instanciation des regex pour récupérer les auteurs et oeuvres (type de catalogue => Rouen 1850-1880)
    auteur = re.compile(r'(^\S[A-Z]{2,})')
    oeuvre = re.compile(r'^(\d{1,3}). \w')

    for entry in dict_entries:
        # Dans un premier temps on récupère l'emplacement de l'auteur et de la première oeuvre dans l'entrée
        num = entry
        text_list = dict_entries[num]
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
        if n_line_auteur == 0 and n_line_oeuvre != 0:
            pass
        elif n_line_auteur != 0 and n_line_oeuvre != 0:
            # vérification que le textblock n'est pas vide et création des balises xml
            n_entree+=1
            root_entry_xml = ET.Element("entry", n=str(n_entree))
            identifiant_entry = title+ "_e"+ str(n_entree)
            root_entry_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_entry
            desc_auteur_xml = ET.SubElement(root_entry_xml, "desc")
            auteur_xml = ET.SubElement(desc_auteur_xml, "name")
            trait_xml = ET.SubElement(desc_auteur_xml, "trait")
            p_trait_xml = ET.SubElement(trait_xml, "p")

            # récupération de la ligne auteur et de ou des lignes trait et intégration dans les balises xml
            n = 0
            liste_trait = []
            dict_desc_item = {}
            for ligne in text_list:
                n += 1
                if n == n_line_auteur:
                    auteur_xml.text = ligne
                elif n < n_line_oeuvre:
                    liste_trait.append(ligne)
                trait_str = "\n".join(liste_trait)
                p_trait_xml.text = trait_str

            # récupération des lignes oeuvres et potentielles lignes informations complémentaires sur l'oeuvre
            # et intégration du titre de l'oeuvre et de son numéro dans l'arbre xml
            for n in range(n_line_oeuvre - 1, len(text_list)):
                if oeuvre.search(text_list[n]):
                    n_oeuvre += 1
                    item_xml = ET.SubElement(root_entry_xml, "item", n=str(n_oeuvre))
                    identifiant_item = identifiant_entry+ "_i"+ str(n_oeuvre)
                    print(type(identifiant_item), identifiant_item)
                    item_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_item
                    num_xml = ET.SubElement(item_xml, "num")
                    title_xml = ET.SubElement(item_xml, "title")
                    num_xml.text = str(n_oeuvre)
                    title_xml.text = re.sub(
                        r'^\d{1,3}.', '', text_list[n])
                    n_ligne_oeuvre = n
                # si les lignes suivantes ne correspondent pas à une oeuvre, on considère qu'il s'agit d'une info
                # et on les stockent donc ensemble sous la forme d'un dictionnaire où chaque clé correspond au
                # numéro de l'oeuvre et chaque valeur aux lignes d'informations
                elif n_ligne_oeuvre < n:
                    if n_oeuvre in dict_desc_item:
                        dict_desc_item[n_oeuvre] = [dict_desc_item[n_oeuvre], text_list[n]]
                    else:
                        dict_desc_item[n_oeuvre] = text_list[n]
                        desc_item_xml = ET.SubElement(item_xml, "desc")
                else:
                    ('LIGNE NON RECONNUE: ', text_list[n])

        # si le dictionnaire d'informations complémentaires est rempli, on insère ses valeurs dans l'arbre xml
            if dict_desc_item:
                desc_xml = root_entry_xml.xpath(".//desc/ancestor::item")
                for el in desc_xml:
                    num_entree = el.xpath(".//num/text()")
                    num_entree_int = int("".join(num_entree))
                    desc_entree = el.find(".//desc")
                    texte_item_entry = str(dict_desc_item[num_entree_int])
                    texte_item_entry = texte_item_entry.replace("[['", "")
                    texte_item_entry = texte_item_entry.replace("', '", "")
                    texte_item_entry = texte_item_entry.replace("'], '", "")
                    texte_item_entry = texte_item_entry.replace("']", "")
                    desc_entree.text = texte_item_entry
            try:
                entrees_page.append(root_entry_xml)
            except Exception:
                print("entrée non ajoutée")
    return [entrees_page, n_entree, n_oeuvre]

