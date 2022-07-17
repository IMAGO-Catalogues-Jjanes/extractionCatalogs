"""
Ce document contient des variables à définir selon les besoins du projet.
Ces variables correspondent au contenu du document TEI en output de la pipeline
"""

# === INSTRUCTIONS XML ====

# Schémas (mettre l'instruction complète en une seule chaîne de caractères ; elle sera parsée par lxml)
schemas = {
    'schema_1': 'href="https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/extractionCatalogs/main/extractionCatalogs/variables/validation_alto/out/ODD_VisualContagions.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"',
    'schema_2': 'href="https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/extractionCatalogs/main/extractionCatalogs/variables/validation_alto/out/ODD_VisualContagions.rng" type="application/xml" schematypens="http://purl.oclc.org/dsdl/schematron"'
}
# lien du schema en ligne, utilisé pour tester la conformité du document TEI produit
lien_schema = "https://raw.githubusercontent.com/IMAGO-Catalogues-Jjanes/extractionCatalogs/main/extractionCatalogs/variables/validation_alto/out/ODD_VisualContagions.rng"

# feuille de style :
CSS = 'type="text/css" href="extractionCatalogs/static/css/affichage_TEI.css"'

# === teiHeader ====

# Événement auquel le catalogue fait référence (OBLIGATOIRE)
# options = artists_group|biennial_triennial_documenta|festival|other|salon|secession|simple_exhibition|society|universal_exhibition|women_artists_exhibition
event_head_type = "salon"
# options = fixed|travelling
event_subtype = "fixed"
# année ou dates :
event_from = "1863"
event_to = ""
if not event_to:
    event_to = event_from

# Projet
name = "VISUAL CONTAGIONS"
persName = "Béatrice Joyeux-Prunel"
orgName = "UNIGE"
addrLine = "5 rue des Battoirs 7"
postCode = "1205"
settlement = "Genève"
date = "2021"
licence = "CC-BY"
licence_target = "https://creativecommons.org/licenses/by/4.0/"

# organisme conservant l'objet numérique (OBLIGATOIRE)
repository = "Bibliothèque nationale de France"

# logiciel utilisé pour la transcription (OBLIGATOIRE)
application_version = "3.1"
application_ident = "kraken"
application_pointer = "https://github.com/mittagessen/kraken"
