import re

expositeur_recuperation_regex = re.compile(r'^.*\)[.]*|^[a-zé]{0,2}[ ]*[a-zé]{0,2}[ ]*[A-ZÉ]+[,]*[ ]*[a-zé]{0,2}[ ]*[a-zé]{0,2}[ ]*[A-ZÉ][a-zé]*[.]*|^[a-zé]{0,2}[ ]*[a-zé]{0,2}[ ]*[A-ZÉ]*[a-zé]*[.,]*[ ]*[a-zé]{0,2}[ ]*[a-zé]{0,2}[ ]*[A-ZÉ]*[a-zé]*[.]*|^[A-ZÉ]*[a-zé][.]*')

oeuvre_recuperation_regex = re.compile(r'^[*]*\d{1,4}[\.][ ](Bis|bis)*[ ]*[—]|^[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[\.]|^[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[—]|[*]*\d{1,4}[ ]*[-]|[*]*\d{1,4}[ ]*(Bis|bis)*[ ]*[–3 ]')

# =================================================================
# Variables ajoutées depuis "Guide – extraction de catalogues.ipynb"
import exemple_ajouts
