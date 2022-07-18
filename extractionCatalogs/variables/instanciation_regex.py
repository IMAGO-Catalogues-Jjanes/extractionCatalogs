"""
Intanciation des regex utilisées pour l'extraction des données.
Supprimer ou ajouter un dièse (#) aux lignes en fonction du type de catalogue

La majeur partie des variables contenant des regex ci dessous sont appelées dans la fonction get_oeuvres()
du fichier extractionCatEntrees_fonctions.py

Pour tester, construire ou obtenir des explications détaillées pour une regex, consulter regex101.com

Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

import re

#####################################################
#  === 1. REGEX LECTURE RAPIDE (ne pas supprimer) ===
# Regex déterminant que des lettres majuscules correspondent à un auteur
auteur_regex = re.compile(r'^[☙]*(\S|[A-Z])[A-ZÉ]{3,}')
# regex déterminant que des chiffres correspondent à une oeuvre
oeuvre_regex = re.compile(r'^[*]*\d{1,4}')
# Regex : extrait le numero de l'oeuvre
numero_regex = re.compile(r'^(\S\d{1,4}|\d{1,4})')
# Regex : auteurs sans prénom ("M. NOM," ou "Mlle NOM," ou "NOM," ou "NOM.")
auteur_sans_prenom_regex = re.compile(r'M(.|[a-z]{2,3}) [A-ZÉa-zé]*|^([A-ZÉ]|-| )*(\.|,| )')
# Regex : premiers caractères d'une ligne entière à identifier
ligne_secondaire_regex = re.compile(r'^([A-ZÉ]|[a-zé])')
# Regex : informations complementaires
info_comp_tiret_parenthese_regex = re.compile(r'—[ ]*.*|\(.*\)|[a-z]\. .*')
# TODO : pas satisfaisant : pas de différence claire entre deuxième ligne et info complémentaire
info_complementaire_regex = re.compile(r'^(\S[A-Z]|[A-Z])[a-z]')
####################################################


#############################################################
#  === 2. REGEX AUTEUR (sélectionner ou créer une nouvelle regex)  ===
# Regex : Nom en majuscules : "NOM (Prénom)," ou "NOM (Initiale.),", ou "NOM (Prénom) ",
# ou "NOM (Initiale.).", ou "NOM, Prénom," ou "NOM, Prénom.", ou "NOM, Prénom ", ou "Nom prénom"
auteur_recuperation_regex = re.compile(r'^.*\)(?=,|\.| |)|^(\S|[A-Z])[A-ZÉ]*[,]* [A-Z][a-zé]*')

# Regex : Nom et prénom avec initiale en majuscule : "Nom Prénom", "Nom", "Prénom"
# auteur_recuperation_regex = re.compile(r'^(\S|[A-ZÉ])[a-z]* [A-Z][a-zé]*|^[A-Z][a-zé]+')

# Regex : auteurs délimités par un cadratin "—" final
#auteur_recuperation_regex = re.compile(r'^.*.(?= —)')
###############################################################


#############################################################
#  === 3. REGEX OEUVRE (sélectionner ou créer une nouvelle regex)  ===

# Regex : oeuvre avec délimitation concrète (".", "–", ". –"=)
# exemples :  "24. Orphée perdant Eurydice", "82. — Paysage", "189 — Lion."
oeuvre_recuperation_regex = re.compile(r'^[*]*\d{1,4}[\.][ ](Bis|bis)*[ ]*[—]|^[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[\.]|^[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[—]|[*]*\d{1,4}[ ]*[-]|[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[–]')

# Regex : oeuvre sans délimitation concrète (cas rares et problématiques : les adresses seront traitées comme des oeuvres et il faudra faire les corrections manuellement)
# exemple : "200 Buttes Chaumont"
# oeuvre_recuperation_regex = re.compile(r'^[*]*\d{1,4}[ ]')
# Cas : cat_inde_1892, 1913, 1923, 1935
#############################################################


#####################################################################################################
#  === 4. REGEX : SEPARATION AUTEUR/INFORMATIONS BIOGRAPHIQUES (sélectionner ou créer une nouvelle regex)  ===

# Regex : "NOM (Prénom), Information biographique"
# limitation_auteur_infobio_regex = re.compile(r'(?:\),).*')
# TODO : celle ci capture aussi les points : (?:\),|\)\.).*

# Regex : "NOM Prénom — Information biographique"
limitation_auteur_infobio_regex = re.compile(r'(— .*)')
#####################################################################################################

