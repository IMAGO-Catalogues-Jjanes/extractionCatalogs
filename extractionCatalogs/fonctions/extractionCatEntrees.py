"""
Extraction des informations contenues dans les fichiers ALTO en sortie de l'OCR
et insertion dans un fichier XML-TEI sur le modèle de l'ODD de Caroline Corbières
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""
import os.path

from .extractionCatEntrees_fonctions import *

# Fonction principale, appelée dans run.py et utilisant les fonctions inclues dans extractionCatEntrees_fonctions.py
def extInfo_Cat(document, typeCat, title, output_file, list_xml, n_entree, n_oeuvre):
    """
    Fonction qui permet, pour un catalogue, d'extraire les différentes données contenues dans le fichier alto en entrée
    et de les insérer dans une arborescence TEI
    :param document: fichier alto parsé par etree
    :type document: lxml.etree._ElementTree
    :param typeCat: type de Catalogue (Nulle: sans information biographique, Simple: avec une information biographique
    sur la ligne en dessous du nom de l'artiste, Double: sur la même ligne que l'auteur et/ou sur d'autres lignes)
    :param title: nom du catalogue à encoder
    :type title:str
    :param output: chemin du fichier TEI en output
    :type output:str
    :param list_xml: ElementTree contenant la balise tei list et les entrées précédemment encodées
    :type list_xml: lxml.etree._ElementTree
    :param n_entree: numéro employé pour l'entrée précédente
    :type n_entree: int
    :param n_oeuvre: numéro employé pour l'oeuvre précédente
    :type n_oeuvre: int
    :return: list_entrees_page
    :rtype: list of lxml.etree._ElementTree
    """

    # === 1. On établit les variables initiales ===
    list_entrees_page = []
    # un compteur pour la liste d'ID qui nous permettra de récupérer les régions des images iiif
    n_iiif = 0

    # === 2.1. On extrait le texte des ALTO ===
    # On récupère un dictionnaire avec pour valeurs les entrées, et une liste d'ID pour couper les images :
    # ( === fonction secondaire appelée dans extractionCatEntrees_fonctions.py === )
    dict_entrees_texte, iiif_regions = get_texte_alto(document)

    # === 2.2. On traite les "EntryEnd", s'il y en a ===
    # on note qu'un document ALTO ne peut avoir qu'un entryEnd, et donc produire qu'un élément pour la liste suivante
    # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
    entree_end_texte = get_EntryEnd_texte(document)
    # Si la liste d'entrées coupées n'est pas vide :
    if entree_end_texte != []:
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
        # (les variables auteur_regex et oeuvre_regex sont importées depuis instanciation_regex.py)
        # TODO Fréderine dit que les entry end ne sont pas intégrées ; vérifier si auteur_regex sert à qqchose ici
        n_line_auteur, n_line_oeuvre = get_structure_entree(entree_end_texte, auteur_regex, oeuvre_regex)
        try:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # TODO c'est ici que ça ne marche pas : pourquoi l'item n'est pas appendé ? on dirait que get_oeuvres ne marche pas
            list_item_entryEnd_xml, n_oeuvre = get_oeuvres(entree_end_texte, title, n_oeuvre, n_entree,
                                                           n_line_oeuvre[0])
            entree_end_xml = list_xml.find(".//entry[@n='" + str(n_entree) + "']")
            for item in list_item_entryEnd_xml:
                entree_end_xml.append(item)
        except Exception:
            a_ecrire = "\n" + str(n_entree) + " " + str(entree_end_texte) + "(entryEnd)"
            with open(os.path.dirname(output_file) + "/" + title + "_problems.txt", mode="a") as f:
                f.write(a_ecrire)

    # === 3.1 On traite les entrées ===
    # pour chaque item du dictionnaire d'entrées du document ALTO :
    for num_entree in dict_entrees_texte:
        # on assigne la valeur de la clé à une variable (c'est une liste avec les lignes constituant une entrée) :
        entree_texte = dict_entrees_texte[num_entree]
        # on récupère les numéros de ligne de l'auteur (int) et des oeuvres (list) dans l'entrée :
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py ===
        n_line_auteur, n_line_oeuvre = get_structure_entree(entree_texte, auteur_regex, oeuvre_regex)
        # TODO Comprendre cette partie du code de Juliette :
        # en commentaire, les lignes condition à activer lorsque l'on s'occupe d'un catalogue entièrement numérisé
        # à la main
        # if num_entree == 0 and n_line_auteur == 0:
        # il s'agit d'une entry normale
        # je créé les balises xml nécessaires par la suite

        # on augmente le compteur en input et en return de la fonction
        n_entree += 1
        # n_iiif est un compteur qu'on utilise pour selectionner des ID indexés dans la liste iiif_regions
        iiif_region = iiif_regions[n_iiif]

        # Nulle = un catalogue ne contient pas d'informations biographiques
        # On indique qu'il n'y a pas d'informations biographiques si le catalogue est de type Nulle
        if typeCat == "Nulle":
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            entree_xml, auteur_xml, p_trait_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region,
                                                                             infos_biographiques=False)
        # Autrement, la fonction part du principe qu'il y a des informations biographiques
        else:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            entree_xml, auteur_xml, p_trait_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region)
        n_iiif += 1

        # === 3.2 On traite les catalogues selon leur type ===
        # on établit un compteur de lignes
        n = 0
        # Nulle = une entrée n'a pas d'informations biographiques
        if typeCat == "Nulle":
            # la ligne entière constitue le nom de l'auteur
            auteur_xml.text = entree_texte[n_line_auteur]
        # Simple = une entrée contient des informations biographiques sur une ligne distincte
        elif typeCat == "Simple":
            # on créé une liste pour indexer des lignes d'information biographique
            liste_trait_texte = []
            # pour chaque chaîne correspondant à une ligne dans la liste de lignes correspondant à une entrée :
            for ligne in entree_texte:
                # on augmente notre compteur de lignes
                n += 1
                # la première ligne doit correspondre à l'auteur
                if n == 1:
                    auteur_xml.text = ligne
                # toutes les lignes antérieurs à celle de la première oeuvre sont des informations biographiques
                # TODO 1 < n pourrait permettre de se passer de la distinction simple et nulle soit separated et mixed
                elif 1 < n < n_line_oeuvre[0]:
                    # on les ajoute à la liste de lignes contenant des informations biographiques
                    liste_trait_texte.append(ligne)
            # on concatène ces chaînes dans la balise p de l'élément trait (information biographique)
            p_trait_xml.text = "\n".join(liste_trait_texte)
            #TODO ici : si p_trait est vide, alors la valeur de la variable devient nulle
        # double = une entrée contient des informations biographiques sur la ligne auteur et sur des lignes distinctes
        elif typeCat == "Double" or typeCat == "Triple":
            liste_trait_texte = []
            for ligne in entree_texte:
                n += 1
                if n == 1:
                    # on utilise les regex pour séparer l'auteur et les informations biographiques
                    auteur_texte = auteur_recuperation_regex.search(ligne)
                    if auteur_texte != None:
                        # "groups() method returns a tuple containing all the subgroups of the match, therefore,
                        # it can return any number of groups that are in a pattern"
                        auteur_xml.text = auteur_texte.group(0)
                    # si la regex ne marche pas, on essaie de voir si le prénom est absent :
                    elif auteur_sans_prenom_regex.search(ligne) != None:
                        auteur_xml.text = auteur_sans_prenom_regex.search(ligne).group(0)

                    # puis on sépare les informations biographiques :
                    info_bio = limitation_auteur_infobio_regex.search(ligne)
                    if info_bio != None:
                        liste_trait_texte.append(info_bio.group(0).replace('),', ''))
                # le reste des lignes avant la première oeuvre seront des informations biographiques
                elif n < n_line_oeuvre[0]:
                    liste_trait_texte.append(ligne)
                # on ajoute ces informations à la balise correspondante
                p_trait_xml.text = "\n".join(liste_trait_texte)
        # TODO si la regex extrait un auteur, et qu'il reste du texte après, ça veut dire que c'est mixé et non separate
        #  peut-être qu'on pourrait ainsi envisager d'enlever complètement les commandes de type de catalogue ?

        # on a a ce stade la balise auteur (name) et informations biographiques (trait/p) complétées
        # on traite les items (oeuvres) :
        try:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # on appelle une fonction qui structure en xml les items :
            list_item_entree, n_oeuvre = get_oeuvres(entree_texte, typeCat, title, n_oeuvre, n_entree, n_line_oeuvre[0])
            # on ajoute ces items à la structure xml :
            for item in list_item_entree:
                entree_xml.append(item)
        except Exception:
            output_txt = "\n" + str(n_entree) + " " + entree_texte + " (entrée)"
            with open(os.path.dirname(output_file) + "/" + title + "_problems.txt", mode="a") as f:
                f.write(output_txt)
        try:
            list_entrees_page.append(entree_xml)
        except Exception:
            print("entrée non ajoutée")

        # TODO : faire en sorte que nous ayons le nom de l'auteur (le récupérer dans une variable), puis les oeuvres
        auteur = entree_texte[n_line_auteur-1]

        # TODO : ceci ne marche pas à tous les coups mais devrait être en principe plus correct :
        # auteur = auteur_xml.xpath("./text()")

        print("\t\t", auteur)
        print("\t\t   auteur : " + str(n_line_auteur) + " ; oeuvres : " + str(n_line_oeuvre))
        print("\t\t   Oeuvres : ", entree_texte)
        print("\t\t   "+lien_iiif)
    if not dict_entrees_texte:
        print("\n\t\tCe fichier ne contient pas d'entrées\n")

    return list_xml, list_entrees_page, n_entree, n_oeuvre
