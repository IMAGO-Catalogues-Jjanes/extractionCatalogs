"""
Intanciation des regex utilisées pour l'extraction des données.
Supprimer ou ajouter un dièse (#) aux lignes en fonction du type de catalogue

Auteur: Juliette Janes
Date: 09/07/21
"""

import re

" Regex pour lecture rapide, à ne pas supprimer "
auteur_regex = re.compile(r'^(\S|[A-Z])[A-ZÉ]{3,}')
oeuvre_regex = re.compile(r'^\d{1,4}')

" Regex pour différents types d'auteurs en fonction du catalogue traité"
# Regex récupérant les auteurs sous la forme NOM (Prénom), ou NOM (Initiale.),
auteur_recuperation_regex = re.compile(r'^.*\),')
# Regex pour les formes se terminant par un cadratin
#auteur_recuperation_regex = re.compile(r'^.*.(?= —)')
# Regex récupérant les auteurs de la forme NOM, Prénom, ou NOM, Prénom. (changer la virgule finale dans la regex par \.)
# auteur_recuperation_regex = re.compile(r'^(\S|[A-Z])[A-ZÉ]*, [A-Z][a-z]*,')
# Regex récupérant les auteurs sous la forme M.NOM, Mlle NOM, (si la forme du catalogue a un point au lieu d'une
# virgule, remplacer la , dans la regex par \.
# auteur_sans_prenom_regex = re.compile(r'M(.|[a-z]{2,3}) [A-ZÉ]*,')
auteur_sans_prenom_regex = re.compile(r'^([A-ZÉ]|-)*(\.|,)')
" Regex pour récupérer les informations biographiques en fonction du catalogue traité"
# Regex récupérant les informations des catalogues de type NOM (Prénom), Information biographique
limitation_auteur_infobio_regex = re.compile(r'(?:\),).*')
# Regex recupérant les informations des catalogues de type NOM Prénom — Information biographique
# limitation_auteur_infobio_regex = re.compile(r'(— .*)')
#Regex à ne pas supprimer
info_complementaire_regex = re.compile(r'^(\S[A-Z]|[A-Z])[a-z]')
ligne_minuscule_regex = re.compile(r'^(\([a-z]|[a-z])')

" Regex pour récupérer les informations concernant l'oeuvre"
# numero de l'oeuvre
numero_regex = re.compile(r'^(\S\d{1,4}|\d{1,4})')
# informations complementaires
info_comp_parentheses_regex = re.compile(r'\(.*\)')
info_comp_tiret_regex = re.compile(r'— .*')