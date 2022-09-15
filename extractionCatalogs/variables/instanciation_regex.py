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
# Regex déterminant que des lettres majuscules correspondent à un exposant
exposant_regex = re.compile(r'^[☙]*(\S|[A-Z])[A-ZÀ-Ǘ]{3,}')
# regex déterminant que des chiffres correspondent à une oeuvre
oeuvre_regex = re.compile(r'^[*]*[ ]*\d{1,4}')
# Regex : extrait le numero de l'oeuvre
numero_regex = re.compile(r'^(\S\d{1,4}|\d{1,4})')
# Regex : une ligne de description, avec la possibilité de commencer par des majuscules
ligne_description_regex = re.compile(r'^[A-ZÀ-Üa-zà-ü-–"&\[{]')
# Regex : informations complémentaires – tout ce qui vienne après une parenthèse ouvrante.
# il existe de nombreuses autres types de délimitations (tirets, points, virgules), mais ces caractères peuvent faire partie des titres des oeuvres
# on préfère donc faire une extraction minimale, les descriptions d'oeuvres étant de manière générale rare, elles devront être extraites manuellement
info_comp_regex = re.compile(r'\(.*|,.*|[^0-9.] —.*')

# Regex  utilisée par le script pour voir si entre parenthèses un trouve un chiffre, dans ce cas on sait que c'est des informations complémentaires
verification_parentheses_regex = re.compile(r'^.*\)')

regex_adresse = re.compile(r'^[*]*\d{1,4}[ bisBIS]*,')
regex_mesures = re.compile(r'^[*]*\d{1,4}[ ]*x')
regex_prix = re.compile(r'^[*]*[0-9]+[\.]*[0-9]* fr[ancs]*[.]*')
####################################################


#############################################################
#  === 2. REGEX AUTEUR (sélectionner ou créer une nouvelle regex)  ===
# Regex : Nom en majuscules : "NOM (Prénom)," ou "NOM (Initiale.),", ou "NOM (Prénom) ",
# ou "NOM (Initiale.).", ou "NOM, Prénom," ou "NOM, Prénom.", ou "NOM, Prénom ", ou "Nom prénom"
exposant_recuperation_regex = re.compile(r"^[MLE .]*[☙]*[ ]*[a-zà-ü]{0,2}[ ]*[a-zà-ü]{0,2}[ ]*[A-ZÀ-ÜŒ\(][,]*[ ]*[A-ZŒÀ-Üa-zœà-ü’`´'.\(\)-]+[, ]*[A-ZŒÀ-Üa-zà-ü]{0,2}[ ]*[VAON ]*[A-ZŒÀ-Ǘ̧̀̂\(\)-][A-Z ŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂’`´'\(\)-]*[ ]*[A-ZŒÀ-Ǘ̧̀̂]*[A-ZŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂’`´'.\(\)-]*[.]*[,]*|^[A-ZŒÀ-Ǘ̀̂a-zœà-ǘ̧̀̂]{0,2}[ ]*[A-ZŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂]{0,2}[ ]*[A-ZŒÀ-Ǘ̧̀̂][A-ZŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂]*[.,]*[ ]*[A-ZŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂]{0,2}[ ]*[A-ZŒÀ-Ǘ̧̀̂a-zœà-ǘ̧̀̂]{0,2}[ ]*[A-ZŒÀ-Ǘ̧̀̂]+[a-zœà-ǘ̀̂]*[.]*[,]*|^[A-ZŒÀ-Ǘ̧̀̂]+[a-zœà-ǘ̧̀̂]*[.]*[,]*")
###############################################################

#############################################################
#  === 3. REGEX OEUVRE (sélectionner ou créer une nouvelle regex)  ===

# Regex : oeuvre avec délimitation concrète (".", "–", ". –"=)
# exemples :  "24. Orphée perdant Eurydice", "82. — Paysage", "189 — Lion."
oeuvre_recuperation_regex = re.compile(r'^[*]*[ ]*\d{1,4}[\.][ ](Bis|bis|ter|Ter|BIS|TER)*[ ]*[—]|^[*]*\d{1,4}[ ]*(Bis|bis|ter|Ter|BIS|TER)*[ ]*[\.]|^[*]*\d{1,4}[ ]*(Bis|bis|ter|Ter|BIS|TER)*[ ]*[—]|[*]*\d{1,4}[ ]*[-]|[*]*\d{1,4}[ ]*(Bis|bis|ter|Ter|BIS|TER)*[ ]*[–]')
#############################################################


