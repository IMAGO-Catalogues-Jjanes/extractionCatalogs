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
    sur la ligne en dessous du nom de l'artiste, Double: sur la même ligne que l'auteur)
    :param title: nom du catalogue à encoder
    :type title:str
    :param output: chemin du fichier TEI en output
    :type output:str
    :param list_xml: ElementTree contenant la balise tei list et les potentielles précédentes entrées encodées
    :type list_xml: lxml.etree._ElementTree
    :param n_entree: numéro employé pour l'entrée précédente
    :type n_entree: int
    :param n_oeuvre: numéro employé pour l'oeuvre précédente
    :type n_oeuvre: int
    :return: entrees_page
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
    list_entree_end_texte = get_EntryEnd_texte(document)
    # Si la liste d'entrées coupées n'est pas vide :
    if list_entree_end_texte != []:
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
        # (les variables auteur_regex et oeuvre_regex sont importées depuis instanciation_regex.py)
        n_line_auteur, n_line_oeuvre = get_structure_entree(list_entree_end_texte, auteur_regex, oeuvre_regex)
        try:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            list_item_entryEnd_xml, n_oeuvre = get_oeuvres(list_entree_end_texte, title, n_oeuvre, n_entree,
                                                           n_line_oeuvre[0])
            entree_end_xml = list_xml.find(".//entry[@n='" + str(n_entree) + "']")
            for item in list_item_entryEnd_xml:
                entree_end_xml.append(item)
        except Exception:
            a_ecrire = "\n" + str(n_entree) + " " + str(list_entree_end_texte)
            with open(os.path.dirname(output_file) + "/" + title + "_problems.txt", mode="a") as f:
                f.write(a_ecrire)

    # === 3. On traite les entrées ===
    # pour chaque item du dictionnaire d'entrées du document ALTO :
    # print(dict_entrees_texte)
    # print(list_entree_end_texte)

    for num_entree in dict_entrees_texte:
        # on assigne la valeur de la clé à une variable (c'est une liste des lignes constituant une entrée) :
        entree_texte = dict_entrees_texte[num_entree]
        # on récupère l'emplacement de l'auteur et de la première oeuvre dans l'entrée
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py ===
        n_line_auteur, n_line_oeuvre = get_structure_entree(entree_texte, auteur_regex, oeuvre_regex)
        # TODO Comprendre à quoi servent ces variables :
        #print(n_line_auteur)
        #print(n_line_oeuvre)
        # TODO Comprendre cette partie du code de Juliette :
        # en commentaire, les lignes condition à activer lorsque l'on s'occupe d'un catalogue entièrement numérisé
        # à la main
        # if num_entree == 0 and n_line_auteur == 0:
        # il s'agit d'une entry normale
        # je créé les balises xml nécessaires par la suite
        n_entree += 1
        iiif_region = iiif_regions[n_iiif]
        if typeCat == "Nulle":
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            entree_xml, auteur_xml, p_trait_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region, infos_biographiques=1)
        else:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            entree_xml, auteur_xml, p_trait_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region)
        n_iiif += 1
        n = 0
        # print("\t\tAUTEUR ", n_line_auteur, "OEUVRES", n_line_oeuvre)
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
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            list_item_entree, n_oeuvre = get_oeuvres(entree_texte, typeCat, title, n_oeuvre, n_entree, n_line_oeuvre[0])
            for item in list_item_entree:
                entree_xml.append(item)
        except Exception:
            output_txt = "\n" + str(n_entree) + " ".join(entree_texte)
            with open(os.path.dirname(output_file) + "/" + title + "_problems.txt", mode="a") as f:
                f.write(output_txt)
        try:
            list_entrees_page.append(entree_xml)
        except Exception:
            print("entrée non ajoutée")

        # auteur + oeuvres (liste, version normale)
        #print("\t\t  ", entree_texte)

        # TODO : faire en sorte que nous ayons le nom de l'auteur (le récupérer dans une variable), puis les oeuvres
        auteur = entree_texte[n_line_auteur-1]
        print("\t\t", auteur)
        print("\t\t   Oeuvres : ", entree_texte)


        print("\t\t   "+lien_iiif)
    if not dict_entrees_texte:
        print("\n\t\tCe fichier ne contient pas d'entrées\n")

    return list_xml, list_entrees_page, n_entree, n_oeuvre
