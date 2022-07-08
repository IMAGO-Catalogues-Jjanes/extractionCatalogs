"""
Ce document contient des variables à définir selon les besoins du projet.
Ces variables correspondent au contenu du document TEI en output de la pipeline
"""

# === INSTRUCTIONS XML ====

# Schémas (mettre l'instruction complète en une seule chaîne de caractères ; elle sera parsée par xml)
schemas = { "schema_1": "indiquez ici un lien vers votre schéma"
}
# lien du schema en ligne, utilisé pour tester la conformité du document TEI produit
lien_schema = ""

# feuille de style :
CSS = ''

# === teiHeader ====

# Événement auquel le catalogue fait référence (OBLIGATOIRE)
# options = artists_group|biennial_triennial_documenta|festival|other|salon|secession|simple_exhibition|society|universal_exhibition|women_artists_exhibition
event_head_type = "OBLIGATOIRE"
# options = fixed|travelling
event_subtype = "OBLIGATOIRE"
# année ou dates :
event_from = "OBLIGATOIRE"
event_to = ""
if not event_to:
    event_to = event_from

# Projet
name = "Nom du projet"
persName = "Directeur ou directrice du projet"
orgName = "Nom de l'organisme"
addrLine = "Adresse de l'organisme"
postCode = ""
settlement = "Ville"
date = "Date du projet"
licence = "Licence"
licence_target = "Lien"

# organisme conservant l'objet numérique (OBLIGATOIRE)
repository = "Organisme conservant l'objet numérique"

# logiciel utilisé pour la transcription (OBLIGATOIRE)
application_version = "OBLIGATOIRE"
application_ident = "OBLIGATOIRE"
application_pointer = "OBLIGATOIRE"
