"""
Extraction des informations contenues dans les fichiers ALTO en sortie de l'OCR
et insertion dans un fichier XML-TEI sur le modèle de l'ODD de Caroline Corbières
Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""
import os.path
import re

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
    # un dictionnaire en return pour signaler des oeuvres
    dict_oeuvres_terminal = {}

    # === 2.1. On extrait le texte de Entry des ALTO ===
    # On récupère un dictionnaire avec pour valeurs les entrées, et une liste d'ID pour couper les images :
    # ( === fonction secondaire appelée dans extractionCatEntrees_fonctions.py === )
    dict_entrees_texte, iiif_regions = get_texte_alto(document)

    # === 2.2. On extrait le texte de entryEnd des ALTO, s'il y en a ===
    # on note qu'un document ALTO ne peut avoir qu'un entryEnd (au tout début)
    # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
    entree_end_texte = get_EntryEnd_texte(document)

    # === 3.1 On traite les "EntryEnd" ===
    # Si la liste n'est pas vide ou qu'elle n'est pas indiquée comme None :
    if entree_end_texte != []:
        if entree_end_texte != None:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # (les variables exposant_regex, oeuvre_regex et oeuvre_recuperation_regex sont importées depuis instanciation_regex.py)
            n_line_exposant, n_line_oeuvre, pas_de_numerotation = get_structure_entree(entree_end_texte, exposant_regex, oeuvre_regex, oeuvre_recuperation_regex)
            try:
                # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
                list_lignes_entryEnd_xml, n_oeuvre, text_name_item_propre, dict_oeuvres_terminal = get_oeuvres(entree_end_texte, title, n_oeuvre, n_entree,
                                                               n_line_oeuvre, pas_de_numerotation)
                # on récupère le numéro d'entrée, qui correspond à l'antérieure car il n'a pas encore été augmenté, pour ajouter les items manquants :
                entree_end_xml = list_xml.find(".//entry[@n='{}']".format(str(n_entree)))
                # si les items ont une numérotation (très grande majorité des cas), on l'ajoute tel qu'il a été produit
                if pas_de_numerotation == False:
                    for ligne in list_lignes_entryEnd_xml:
                        entree_end_xml.append(ligne)
                # si ce n'est pas le cas, cette numérotation sera artificielle ; on reprend l'attribut "@n" de l'item précédent :
                elif pas_de_numerotation == True:
                    for ligne in list_lignes_entryEnd_xml:
                        numero_anterieur = list_xml.xpath("//entry[@n='{}']/item[last()]/@n".format(str(n_entree)))
                        # on récupère une liste qu'on va transformer en chaine et nettoyer pour ne garder que le numéro :
                        numero_anterieur = str(numero_anterieur)
                        numero_anterieur = nettoyer_liste_str(numero_anterieur)
                        # on actualise le numéro :
                        numero_nouveau = int(numero_anterieur) + 1
                        # on retransforme en chaine, puisque cela est nécessaire pour faire la méthode .attrib
                        numero_nouveau = str(numero_nouveau)
                        ligne.attrib["n"] = numero_nouveau

                        # on va aussi changer la terminaison de l'ID pour l'actualiser :
                        terminaison_id_ancienne = ligne.attrib["{http://www.w3.org/XML/1998/namespace}id"][-3:]
                        id = ligne.attrib["{http://www.w3.org/XML/1998/namespace}id"]
                        terminaison_id_nouvelle = id.replace(terminaison_id_ancienne, "_i{}".format(numero_nouveau))
                        ligne.attrib["{http://www.w3.org/XML/1998/namespace}id"] = terminaison_id_nouvelle

                        entree_end_xml.append(ligne)
            except Exception:
                a_ecrire = str(entree_end_texte) + "[(entrée {}])".format(n_entree)
                entryend_non_integree_liste.append(a_ecrire)
                entryend_non_integree = True
                print("\t    [!] L'entryEnd suivante n'a pas été extraite :")
                for ligne in entree_end_texte:
                    print("\t    " + nettoyer_liste_str(str(ligne)))
                    # On rajoute un saut de ligne pour la dernière ligne de l'entryEnd, afin de la différencier clairement de l'extraction sur le terminal
                    if ligne == entree_end_texte[-1]:
                        barre = "\t    "
                        for caractere in ligne:
                            barre += "-"
                        print(barre + "\n")
        # on indique sur le terminal les oeuvres de cette entryEnd :
        if dict_oeuvres_terminal:
            for oeuvre in dict_oeuvres_terminal:
                print("\t\t  " + oeuvre)
                if dict_oeuvres_terminal[oeuvre] :
                    print("\t\t      " + str(dict_oeuvres_terminal[oeuvre]))


    # === 3.2 On traite les "Entry" ===
    # pour chaque item du dictionnaire d'entrées du document ALTO :
    for num_entree in dict_entrees_texte:
        # on assigne la valeur de la clé à une variable (c'est une liste avec les lignes constituant une entrée) :
        entree_texte = dict_entrees_texte[num_entree]
        # on augmente le compteur en input et en return de la fonction
        n_entree += 1
        # n_iiif est un compteur qu'on utilise pour selectionner des ID indexés dans la liste iiif_regions
        iiif_region = iiif_regions[n_iiif]

        # on récupère le numéro de ligne de l'exposant (int) et ceux des oeuvres (list) dans l'entrée :
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py ===
        n_line_exposant, n_line_oeuvre, pas_de_numerotation = get_structure_entree(entree_texte, exposant_regex, oeuvre_regex, oeuvre_recuperation_regex)
        # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
        entree_xml, desc_exposant_xml, exposant_xml, lien_iiif = create_entry_xml(document, title, n_entree, iiif_region)
        n_iiif += 1

        # === 3.2 On traite les exposantS et leurs éventuelles informations complémentaires ===
        # on établit un compteur de lignes
        n = 0
        liste_trait_texte = []
        # on assigne la regex de récupération d'auteur à une variable nouvelle, puisqu'il sera question de détérminer s'il faut la garder ou pas
        exposant_recuperation_regex_courante = exposant_recuperation_regex
        for ligne in entree_texte:
            n += 1
            # la ligne 1 est celle de l'exposant
            if n == 1:
                if "☙" in ligne:
                    ligne.replace("☙", "")
                # on va d'abord regarder s'il y a des chiffres entre parenthese ; dans ce cas, il est certain
                # que les parenthèse ne contiennent pas de non/prenom, mais des informations complémentaires, et il faut adapter la regex
                verification_parentheses = verification_parentheses_regex.search(ligne)
                # s'il y a des parenthèses
                if verification_parentheses:
                    verification_parentheses_text = verification_parentheses.group(0)
                    # on créé une petite regex qui vérifie s'il y a un ou plusieurs chiffres dans le texte
                    chiffres_regex = re.compile(r'[0-9]+')
                    chifres_presents = chiffres_regex.search(verification_parentheses_text)
                    # s'il y a des chiffres avant la fermeture des parenthèses :
                    if chifres_presents:
                        # on assigne à la variable de récupération de l'exposant une nouvelle regex, qui met de côté les informatiosn entre parenthèses
                        # Cette nouvelle regex est tout simplement la même, sur laquelle on enleverra toutes les occurences de "\(" (parenthèse ouvrante échappée)
                        # la méthode .pattern permet de récupérer une regex qui avait été compilée
                        exposant_recuperation_regex_string = exposant_recuperation_regex.pattern
                        exposant_recuperation_regex_parentheses_enlevees = exposant_recuperation_regex_string.replace("\(", "")
                        exposant_recuperation_regex_courante = re.compile(exposant_recuperation_regex_parentheses_enlevees)

                # si on détecte la mention ", né[e] à ", on va faire adapter le traitement pour que les résultats soient meilleurs
                regex_naissance = re.compile(r', [Nn]+é[e]* à .*|, [Nn]+é[e]* à .*|, [Nn]+é[e]* à .*')
                # on utilise les regex pour séparer l'exposant des éventuelles informations biographiques
                if regex_naissance.search(ligne):
                    exposant_texte = re.sub(regex_naissance, "", ligne)
                # si non, on fait le traitement normal :
                else:
                    exposant_texte = exposant_recuperation_regex_courante.search(ligne)
                    if exposant_texte != None:
                        exposant_texte = exposant_texte.group(0)
                # si on obtient un résultat :
                if exposant_texte != None:
                    # "group() method returns a tuple containing all the subgroups of the match, therefore,
                    # it can return any number of groups that are in a pattern"
                    exposant_xml.text = exposant_texte
                    print("\t      " + exposant_texte)
                # on utilise la même regex pour isoler tout le texte restant, s'il y en a
                # d'abord, s'il y a la mention la mention ", né[e] à " :
                if regex_naissance.search(ligne):
                    info_bio = regex_naissance.search(ligne).group(0)
                    liste_trait_texte.append(info_bio)
                # si non, on fait le traitement normal :
                else:
                    # mais la variable est une regex compilée ; on peut heureusement récupèrer la regex originale avec la méthode .pattern
                    exposant_recuperation_regex_originale = exposant_recuperation_regex_courante.pattern
                    info_bio = re.sub(r"{}".format(exposant_recuperation_regex_originale), '', ligne)
                    if info_bio != None:
                        if info_bio != "":
                            # on enlève les espaces de début, puisqu'il y en a souvent :
                            re.sub(r'^[ ]*[ ]*', '', info_bio )
                            liste_trait_texte.append(info_bio)
            # le reste des lignes avant la première oeuvre seront des informations biographiques
            elif n > 1:
                if n_line_oeuvre:
                    if n < n_line_oeuvre[0]:
                        liste_trait_texte.append(ligne)
        # si la liste d'informations complémentaires contient quelque chose :
        if liste_trait_texte:
            # on créé les balises pour la description :
            trait_xml = ET.SubElement(desc_exposant_xml, "trait")
            p_trait_xml = ET.SubElement(trait_xml, "p")
            # on unit toutes les chaînes de la liste :
            liste_trait_texte_propre = " ".join(liste_trait_texte)
            liste_trait_texte_propre = liste_trait_texte_propre.replace("¬ ", "")
            # on met la nouvelle chaîne dans la balise "p" :
            p_trait_xml.text = liste_trait_texte_propre
            # on affiche les informations complémentaires sur le terminal :
            print("\t      " + liste_trait_texte_propre)

        # === 3.2 On traite les OEUVRES et leurs éventuelles informations complémentaires  ===
        try:
            # === fonction secondaire appelée dans extractionCatEntrees_fonctions.py : ===
            # on appelle une fonction qui structure en xml les items :
            list_item_entree, n_oeuvre, text_name_item_propre, dict_oeuvres_terminal = get_oeuvres(entree_texte, title, n_oeuvre, n_entree, n_line_oeuvre, pas_de_numerotation)
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

        # on indique sur le terminal les oeuvres
        if dict_oeuvres_terminal:
            for oeuvre in dict_oeuvres_terminal:
                print("\t\t  " + oeuvre)
                # si l'oeuvre a une description, on l'indique sur le terminal (si la valeur n'est pas None)
                if dict_oeuvres_terminal[oeuvre]:
                    print("\t\t      " + str(dict_oeuvres_terminal[oeuvre]))

        # on indique un lien vers l'image iiif si elle existe:
        if lien_iiif:
            print("\t\t  " + "Image : " + lien_iiif)

    # si le dictionnaire d'entrées est vide, on indique sur le terminal que le fichier ne contient pas d'entrées
    if not dict_entrees_texte:
        print("\n\t\tCe fichier ne contient pas d'entrées\n")

    return list_xml, list_entrees_page, n_entree, n_oeuvre, entryend_non_integree, entry_non_integree, entryend_non_integree_liste, entry_non_integree_liste
