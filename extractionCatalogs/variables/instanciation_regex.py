"""
Intanciation des regex utilisées pour l'extraction des données.
Supprimer ou ajouter un dièse (#) aux lignes en fonction du type de catalogue

La majeur partie des variables contenant des regex ci dessous sont appelées dans la fonction get_oeuvres()
du fichier extractionCatEntrees_fonctions.py

Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

import re

#  === 1. REGEX LECTURE RAPIDE (ne pas supprimer) ===
auteur_regex = re.compile(r'^(\S|[A-Z])[A-ZÉ]{3,}')
oeuvre_regex = re.compile(r'^\d{1,4}')


#  === 2. REGEX AUTEURS (en fonction du catalogue traité)  ===

# Regex : test pour catalogues expos universelles (auteur numéroté)
# auteur_recuperation_regex = re.compile(r'^.*\),')

# Regex : "NOM (Prénom)," ou "NOM (Initiale.),", ou "NOM (Prénom)", ou "NOM (Initiale.)."
# TODO Pour exclure la virgule, utiliser '^.*\)(?=,'
auteur_recuperation_regex = re.compile(r'^.*\)[,.]')

# Regex : auteurs délimités par un cadratin "—" final
#auteur_recuperation_regex = re.compile(r'^.*.(?= —)')

# Regex : "NOM, Prénom," ou "NOM, Prénom.", ou "NOM, Prénom "  (changer la virgule finale dans la regex par \.)
# auteur_recuperation_regex = re.compile(r'^(\S|[A-Z])[A-ZÉ]*, [A-Z][a-z]*,')
# TODO : marche mieux ^(\S|[A-Z])[A-ZÉ]*, [A-Z][a-zé]*[,. ]

# Regex : "M. NOM," "Mlle NOM," (pour remplacer la "," finale par "." remplacer "," par "\." dans la regex
# auteur_sans_prenom_regex = re.compile(r'M(.|[a-z]{2,3}) [A-ZÉ]*,')

# Regex : "NOM," ou "NOM."
# TODO : mieux : ^([A-ZÉ]|-| )*(\.|,| )
auteur_sans_prenom_regex = re.compile(r'^([A-ZÉ]|-)*(\.|,)')


#  === 3. REGEX : SEPARATION AUTEUR/INFORMATIONS BIOGRAPHIQUES (en fonction du catalogue traité)  ===

# TODO regex pour rues
# options : repérer mot "rue", "av." etc.
# - vérifier si la numérotation est conforme (+ 1 ou égal à l'item antérieur)

# Regex : "NOM (Prénom), Information biographique"
# limitation_auteur_infobio_regex = re.compile(r'(?:\),).*')
# TODO : celle ci capture aussi les points : (?:\),|\)\.).*

# Regex : "NOM Prénom — Information biographique"
limitation_auteur_infobio_regex = re.compile(r'(— .*)')

# Regex à ne pas supprimer
info_complementaire_regex = re.compile(r'^(\S[A-Z]|[A-Z])[a-z]')
ligne_minuscule_regex = re.compile(r'^(\([a-z]|[a-z])')



#  === 4. REGEX OEUVRE (en fonction du catalogue traité)  ===

# Regex : numero de l'oeuvre
numero_regex = re.compile(r'^(\S\d{1,4}|\d{1,4})')

# Regex : informations complementaires
info_comp_parentheses_regex = re.compile(r'\(.*\)')
info_comp_tiret_regex = re.compile(r'— .*')