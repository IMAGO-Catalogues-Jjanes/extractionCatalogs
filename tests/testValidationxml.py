"""
Script de test permettant de vérifier l'adéquation du fichier xml produit avec l'ODD du projet créé par Caroline Corbières

Author: Juliette Janes
Date: 21/06/21
"""
import sys
import unittest
from lxml import etree as ET

def association_xml_rng(schema_rng, document_xml):
    """
    Fonction qui ajoute le schéma rng au document xml tei afin de vérifier leur adéquation.
    :param schema_rng: schéma RelaxNG comprenant la structure définie dans l'ODD du projet (NDF_ODD.xml)
    :type schema_rng: str
    :param document_xml: fichier xml tei de travail parsé par etree
    :type document_xml: str
    :return resultat: chaîne de caractères validant le fichier xml tei
    :type resultat:str
    """
    # on parse le document xml pour le récupérer
    try:
        fichier_xml = etree.parse(document_xml)
    except etree.XMLSyntaxError:
        # si il y a une erreur au niveau du xml du fichier, on le signale et on arrête le programme.
        print("Le fichier xml n'est pas bien formé.")
        sys.exit()

    # récupération et parsage en tant que relaxng du fichier rng
    relaxng_fichier = etree.parse(schema_rng)
    relaxng = etree.RelaxNG(relaxng_fichier)

    # association du relaxng et du fichier tei
    if relaxng(fichier_xml):
        # si le document est valide on stocke dans la variable resultat une chaîne de caractère validant le document
        resultat= "tei valide"
        print("Le document XML est conforme au schéma TEI et à l'ODD du projet.")
    else:
        # sinon on signale que le document n'est pas valide et on ajoute les messages d'erreurs
        print("Le document XML n'est pas conforme au schéma TEI et à l'ODD du projet." + relaxng.assertValid(xml_tei_valide))

    return resultat

class Validation_rng(unittest.TestCase):
    """
    Classe permettant la validation du fichier tei
    """
    def setUp(self, titre_fichier):
        """ Initialisation du test"""

        self.xml = titre_fichier
        self.rng = './out/ODD_VisualContagions.rng'

    print("Test de validité du fichier TEI \n")

    def test_rng(self):
        """ Permet de tester la fonction validation"""
        self.assertEqual(association_xml_rng(self.rng, self.xml), "tei valide")


if __name__ =='__main__':
    unittest.main()