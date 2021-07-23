from fonctions.instanciation_regex import *
from fonctions.extractionCatEntrees import *
from fonctions.creationTEIheader import *
def get_oeuvres(texte_items_liste, titre, id_n_oeuvre, id_n_entree, n_line_oeuvre):
    list_item_ElementTree = []
    dict_item_texte = {}
    dict_item_desc_texte = {}
    # pour chaque ligne de la 1er ligne oeuvre, à la fin de l'entrée
    for n in range(n_line_oeuvre, len(texte_items_liste)):
        current_line = texte_items_liste[n]
        if oeuvre_regex.search(current_line):
            id_n_oeuvre += 1
            item_xml = ET.Element("item", n=str(id_n_oeuvre))
            list_item_ElementTree.append(item_xml)
            identifiant_item = titre + "_e" + str(id_n_entree) + "_i" + str(id_n_oeuvre)
            item_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = identifiant_item
            num_xml = ET.SubElement(item_xml, "num")
            title_xml = ET.SubElement(item_xml, "title")
            num_xml.text = str(id_n_oeuvre)
            dict_item_texte[id_n_oeuvre] = current_line
            n_line_item = n
        elif n - 1 == n_line_item and ligne_minuscule_regex.search(current_line):
            dict_item_texte[id_n_oeuvre] = [dict_item_texte[id_n_oeuvre], current_line]
        elif n_line_item < n and info_complementaire_regex.search(current_line):
            dict_item_desc_texte[id_n_oeuvre] = current_line
            desc_item_xml = ET.SubElement(item_xml, "desc")
        elif id_n_oeuvre in dict_item_desc_texte:
            dict_item_desc_texte[id_n_oeuvre] = [dict_item_desc_texte[id_n_oeuvre], current_line]
        else:
            ('LIGNE NON RECONNUE: ', current_line)

    for el in list_item_ElementTree:
        num_item = int("".join(el.xpath(".//num/text()")))
        name_item = el.find(".//title")
        texte_name_item = str(dict_item_texte[num_item])
        texte_name_item_propre = nettoyer_liste_str(texte_name_item)
        name_item.text = re.sub(r'^(\S\d{1,3}|\d{1,3}).', '', texte_name_item_propre)
        if el.xpath(".//desc"):
            desc_item = el.find(".//desc")
            texte_desc_item = str(dict_item_desc_texte[num_item])
            desc_item.text = nettoyer_liste_str(texte_desc_item)

    return list_item_ElementTree, id_n_oeuvre


def get_entries(texte, title, typeCat, n_line_oeuvre, n_entree=0, n_oeuvre=0, list_entrees_page=[]):

    n_entree = n_entree + 1
    if typeCat == "Nulle":
        entree_xml, auteur_xml, p_trait_xml = create_entry_xml(title, n_entree, infos_biographiques=1)
    else:
        entree_xml, auteur_xml, p_trait_xml = create_entry_xml(title, n_entree)
    n = 0
    if typeCat == "Nulle":
        auteur_xml.text = texte[0]
    elif typeCat == "Simple":
        liste_trait_texte = []
        for ligne in texte:
            n += 1
        if n == 0:
            auteur_xml.text = ligne
        elif n < n_line_oeuvre:
            liste_trait_texte.append(ligne)
        p_trait_xml.text = "\n".join(liste_trait_texte)
    elif typeCat == "Double":
        liste_trait_texte = []
        for ligne in texte:
            n += 1
            if n == 0:
                auteur_texte = auteur_recuperation_regex.search(ligne)
                if auteur_texte == None:
                    auteur_sans_prenom = auteur_sans_prenom_regex.search(ligne)
                    auteur_xml.text = auteur_sans_prenom.group(0)
                else:
                    auteur_xml.text = auteur_texte.group(0)
                info_bio = limitation_auteur_infobio_regex.search(ligne)
                if info_bio != None:
                    liste_trait_texte.append(info_bio.group(0).replace('),', ''))

            elif n < n_line_oeuvre:
                liste_trait_texte.append(ligne)
            p_trait_xml.text = "\n".join(liste_trait_texte)

    list_item_entree, n_oeuvre = get_oeuvres(texte, title, n_oeuvre, n_entree, n_line_oeuvre)
    for item in list_item_entree:
        entree_xml.append(item)
    try:
        list_entrees_page.append(entree_xml)
    except Exception:
        print("entrée non ajoutée")

    return list_entrees_page, n_entree, n_oeuvre

document = "./test.txt"
with open(document, mode="r") as f:
    texte_page = f.read()
Line_list = texte_page.split("\n")
titre_catalogue = "CatNancy_1892"
#création des balises tei, application du teiHeader et ajout, création des balises body-text-list
root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titre_catalogue
teiHeader_xml = creation_header()
root_xml.append(teiHeader_xml)
text_xml = ET.SubElement(root_xml, "text")
body_xml = ET.SubElement(text_xml, "body")
list_xml = ET.SubElement(body_xml, "list")

n=0
line_debut_entree_list = []
first_oeuvre_line = None
for line in Line_list:
    if auteur_regex.search(line):
        line_debut_entree_list.append(n)
    elif oeuvre_regex.search(line):
        if first_oeuvre_line == None:
            first_oeuvre_line = n
            print(line)
    else:
        pass
    n+=1
if line_debut_entree_list[0]!=0:
    pass
else:
    num=0
    for n in range(len(line_debut_entree_list)):
        num+=1
        try:
            line_debut_entree = line_debut_entree_list[n]
            line_fin_entree = line_debut_entree_list[n + 1]
            print(line_debut_entree, line_fin_entree)
            Entree_Liste_Texte = Line_list[line_debut_entree:line_fin_entree]
            if num ==1:
                liste_entree_page, n_entree, n_oeuvre = get_entries(Entree_Liste_Texte, "Titre", "Double",
                                                                    n_line_oeuvre=first_oeuvre_line)
            else:
                liste_entree_page, n_entree, n_oeuvre = get_entries(Entree_Liste_Texte, "Titre", "Double",
                                                                    n_line_oeuvre=first_oeuvre_line,
                                                                    n_entree=n_entree, n_oeuvre=n_oeuvre,
                                                                    list_entrees_page=liste_entree_page)
        except:
            line_debut_entree = line_debut_entree_list[n]
            line_fin_entree = len(Line_list)
            print(line_debut_entree, line_fin_entree)
            Entree_Liste_Texte = Line_list[line_debut_entree:line_fin_entree]
            liste_entree_page, n_entree, n_oeuvre = get_entries(Entree_Liste_Texte, "Titre", "Double",
                                                                n_line_oeuvre=first_oeuvre_line,
                                                                n_entree=n_entree, n_oeuvre=n_oeuvre,
                                                                list_entrees_page=liste_entree_page)
    print(liste_entree_page)
    for el in liste_entree_page:
        list_xml.append(el)

#comparer avec le list_xml obtenu pour avec les entrées.
ET.ElementTree(root_xml).write("resultat_texte.xml",encoding="UTF-8",xml_declaration=True)