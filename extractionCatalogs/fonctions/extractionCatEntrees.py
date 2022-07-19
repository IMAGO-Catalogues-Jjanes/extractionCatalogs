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
def extInfo_Cat(document, title, list_xml, n_entree, n_oeuvre):
    """
    Fonction qui permet, pour un catalogue, d'extraire les différentes données contenues dans le fichier alto en entrée
    et de les insérer dans une arborescence TEI
    :param document: fichier alto parsé par etree
    :type document: lxml.etree._ElementTree
    :param title: nom du catalogue à encoder
    :type title:str
    :param list_xml: ElementTree contenant la balise tei list et les entrées précédemment encodées
    :type list_xml: lxml.etree._ElementTree
    :param n_entree: numéro employé pour l'entrée précédente / fonctionne dès lors comme index pour l'entrée courante
    :type n_entree: int
    :param n_oeuvre: numéro employé pour l'oeuvre précédente / fonctionne dès lors comme index pour l'oeuvre courante
    :type n_oeuvre: int
    :return: list_entrees_page
    :rtype: list of lxml.etree._ElementTree
    """

    # === 1. On établit les variables initiales ===
    list_entrees_page = []
    # on établit des listes pour récupérer des entry et entryEnd non intégrées et les ajouter au fichier problemes.txt
    entry_non_integree_liste = []
    entryend_non_integree_liste = []
    # un compteur relatif aux index de la liste d'ID qui nous permettra de récupérer les régions des images iiif
    n_iiif = 0
    # on établit deux variables utilisées postérieurement pour indiquer sur le terminal combien d'entry et d'entryEnd non pas été correctement traitées
    entry_non_integree = False
    entryend_non_integree = False

    # === 2.1. On extrait le texte de Entry des ALTO ===
    # On récupère un dictionnaire avec pour valeurs les entrées, et une liste d'ID pour couper les images :
    # ( === fonction secondaire appelée dans extractionCatEntrees_fonctions.py === )
    dict_entrees_texte, iiif_regions = get_texte_alto(document)

    # === 2.2. On extrait le texte de entryEnd des ALTO, s'il y en a ===
    # on note qu'un document ALTO ne peut avoir qu'un entryEnd (au tout début)
    # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
    entree_end_texte = get_EntryEnd_texte(document)

    # Si la liste n'est pas vide ou qu'elle n'est pas indiquée comme None :
    if entree_end_texte != []:
        if entree_end_texte != None:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # (les variables auteur_regex, oeuvre_regex et oeuvre_recuperation_regex sont importées depuis instanciation_regex.py)
            n_line_auteur, n_line_oeuvre = get_structure_entree(entree_end_texte, auteur_regex, oeuvre_regex, oeuvre_recuperation_regex)
            try:
                # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
                list_lignes_entryEnd_xml, n_oeuvre, text_name_item_propre, liste_oeuvres_terminal = get_oeuvres(entree_end_texte, title, n_oeuvre, n_entree,
                                                               n_line_oeuvre[0])
                # on récupère le numéro d'entrée, qui correspond à l'antérieure car il n'a pas encore été augmenté, pour ajouter les items manquants :
                entree_end_xml = list_xml.find(".//entry[@n='" + str(n_entree) + "']")
                for ligne in list_lignes_entryEnd_xml:
                    entree_end_xml.append(ligne)
            except Exception:
                a_ecrire = str(entree_end_texte) + "[(entrée {}])".format(n_entree)
                entryend_non_integree_liste.append(a_ecrire)
                entryend_non_integree = True

    # === 3.1 On traite les "Entry" ===
    # pour chaque item du dictionnaire d'entrées du document ALTO :
    for num_entree in dict_entrees_texte:
        # on assigne la valeur de la clé à une variable (c'est une liste avec les lignes constituant une entrée) :
        entree_texte = dict_entrees_texte[num_entree]
        # on augmente le compteur en input et en return de la fonction
        n_entree += 1
        # n_iiif est un compteur qu'on utilise pour selectionner des ID indexés dans la liste iiif_regions
        iiif_region = iiif_regions[n_iiif]

        # on récupère le numéro de ligne de l'auteur (int) et ceux des oeuvres (list) dans l'entrée :
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py ===
        n_line_auteur, n_line_oeuvre = get_structure_entree(entree_texte, auteur_regex, oeuvre_regex, oeuvre_recuperation_regex)

        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
        entree_xml, desc_auteur_xml, auteur_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region)
        n_iiif += 1

        # === 3.2 On traite les AUTEURS et leurs éventuelles informations complémentaires ===
        # on établit un compteur de lignes
        n = 0
        liste_trait_texte = []
        for ligne in entree_texte:
            n += 1
            # la ligne 1 est celle de l'auteur
            if n == 1:
                # on utilise les regex pour séparer l'auteur des éventuelles informations biographiques
                auteur_texte = auteur_recuperation_regex.search(ligne)
                # si on obtient un résultat :
                if auteur_texte != None:
                    # "group() method returns a tuple containing all the subgroups of the match, therefore,
                    # it can return any number of groups that are in a pattern"
                    auteur_texte = auteur_texte.group(0)
                    auteur_xml.text = auteur_texte
                    print("\t      " + auteur_texte)
                # on utilise la même regex pour isoler tout le texte restant, s'il y en a
                # ATTENTION : la regex suivante doit correspondre à la variable "auteur_recuperation_regex", qui ne peut pas être indiquée en tant que variable
                info_bio = re.sub(r'^.*\)[.]*|^[a-z]{0,2}[ ]*[a-z]{0,2}[ ]*[A-Z][A-ZÉ]*[,]*[ ]*[a-z]{0,2}[ ]*[a-z]{0,2}[ ]*[A-Z][a-zé]*[.]*|^[a-z]{0,2}[ ]*[a-z]{0,2}[ ]*[A-ZÉ]*[a-zé]*[.,]*[ ]*[a-z]{0,2}[ ]*[a-z]{0,2}[ ]*[A-Z]*[a-zé]*[.]*|^[A-ZÉ]*[a-zé][.]*', '', ligne)
                # texte_name_item_propre = re.sub(r'^(\S\d{1,3}|\d{1,3})[.]*[ ]*[—]*[ ]*', '', texte_name_item_propre)
                if info_bio != None:
                    liste_trait_texte.append(info_bio.replace('),', ''))
            # le reste des lignes avant la première oeuvre seront des informations biographiques
            elif 1 < n < n_line_oeuvre[0]:
                liste_trait_texte.append(ligne)
        # si la liste d'informations complémentaires contient quelque chose :
        if liste_trait_texte:
            # des fois, au lieu de none, la valeur sera une chaîne vide, on met cela de côté également :
            if liste_trait_texte[0] != '':
                trait_xml = ET.SubElement(desc_auteur_xml, "trait")
                p_trait_xml = ET.SubElement(trait_xml, "p")
                liste_trait_texte_propre = " ".join(liste_trait_texte)
                p_trait_xml.text = liste_trait_texte_propre
                print("\t      " + liste_trait_texte_propre)

        # === 3.2 On traite les OEUVRES et leurs éventuelles informations complémentaires  ===
        try:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # on appelle une fonction qui structure en xml les items :
            list_item_entree, n_oeuvre, text_name_item_propre, liste_oeuvres_terminal = get_oeuvres(entree_texte, title, n_oeuvre, n_entree, n_line_oeuvre[0])
            # on ajoute ces items à la structure xml :
            for item in list_item_entree:
                entree_xml.append(item)
        except Exception:
            # Si l'entrée n'est pas ajoutée, on indique cela dans une chaine qui sera intégrée au fichier problemes.txt
            output_txt = str(entree_texte) + " [(entrée {})]".format(str(n_entree))
            entry_non_integree_liste.append(output_txt)
            entry_non_integree = True

        try:
            list_entrees_page.append(entree_xml)
        except Exception:
            print("entrée non ajoutée")

        # on indique sur le terminal les oeuvres et un lien vers l'image iiif :
        for oeuvre in liste_oeuvres_terminal:
            print("\t\t  " + oeuvre)
        print("\t\t  " + "Image : " + lien_iiif)

    # si le dictionnaire d'entrées est vide, on indique sur le terminal que le fichier ne contient pas d'entrées
    if not dict_entrees_texte:
        print("\n\t\tCe fichier ne contient pas d'entrées\n")

    return list_xml, list_entrees_page, n_entree, n_oeuvre, entryend_non_integree, entry_non_integree, entryend_non_integree_liste, entry_non_integree_liste
