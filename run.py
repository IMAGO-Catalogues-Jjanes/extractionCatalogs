"""
Initialisation du programme
Programme permettant, à partir de catalogues d'expositions océrisés avec Kraken, d'extraire les données contenues
dans le fichier de sortie de l'OCR (ALTO4 XML), et de construire un fichier TEI sur le modèle de l'ODD défini par
Caroline Corbières (https://github.com/carolinecorbieres/ArtlasCatalogues/blob/master/5_ImproveGROBIDoutput/ODD/ODD_Transformation.xml)

Le programme est particulièrement adapté à un traitement à partir d'eScriptorium, une interface pour kraken permettant de visualiser
le processus de segmentation puis d'obtenir les fichier ALTO4 nécessaires à cette pipeline.

Author: Juliette Janes
Date: 11/06/21
Continué par Esteban Sánchez Oeconomo 2022
"""

# === 1.1 On appelle les paquets externes, modules et fonctions nécessaires ====
# paquets
from lxml import etree as ET
import os
import click
# modules
from extractionCatalogs.fonctions.extractionCatEntrees import extInfo_Cat
from extractionCatalogs.fonctions.creationTEI import creation_header
from extractionCatalogs.fonctions.restructuration import restructuration_automatique
from extractionCatalogs.fonctions.validation_alto.test_Validations_xml import check_strings, get_entries
from extractionCatalogs.fonctions.automatisation_kraken.kraken_automatic import transcription
from extractionCatalogs.variables import contenu_TEI


# === 1.2 Création des commandes pour lancer le script sur le Terminal ====
# E: commandes obligatoires :
@click.command()
@click.argument("directory", type=str)
@click.argument("output", type=str, required=True)
@click.argument("typecat", type=click.Choice(['Nulle', "Simple", "Double", "Triple"]), required=True)
# E : options
@click.option("-n", "--name", "titlecat", type=str,
              help="Select a custom name for the catalog id in the TEI output. By default, it takes the output name")
@click.option("-st", "--segtrans", "segmentationtranscription", is_flag=True, default=False,
              help="automatic segmentation and transcription via kraken. Input files must be images.")
@click.option("-v", "--verify", "verifyalto", is_flag=True, default=False,
              help="verify ALTO4 input files conformity and structure")
# E : La commande "python3 run.py" lance la fonction extraction, qui reprend les variables indiquées sur le terminal :
def extraction(directory, output, typecat, titlecat, verifyalto, segmentationtranscription):
    """
    Python script taking a directory containing images or alto4 files of exhibition catalogs in input and giving back an
    XML-TEI encoded catalog

    directory: path to the directory containing images or alto4 files
    output: name of the TEI file output
    typeCat: catalog's type according to the division done in the github of the project (Nulle, Simple, Double or Triple)
    titlecat: name of the processed catalog. It takes the output name by default but can be customized with -n command
    -st: take image files as an input instead of ALTO4. Automatic segmentation and transcription occurs via kraken.
    -v: verify ALTO4 files.
    """

# === 1.3 Options activées/désactivées ====
    # E : si aucun nom n'a été donné au catalogue avec la commande -n, il prend pour nom la valeur de l'output choisi :
    if not titlecat:
        titlecat = output
        # E : si le nom de l'output contient une extension ".xml", on l'enlève
        if titlecat.__contains__(".xml"):
            titlecat = titlecat[:-3]
        else:
            pass
    else:
        pass

    # E : si l'on souhaite segmenter et océrriser automatiquement (-st) :
    # TODO : les commandes kraken ne semblent plus d'actualité ; vérifier fonction
    if segmentationtranscription:
        print("Segmentation et transcription automatiques en cours")
        # E : on appelle le module transcription (fichier kraken_automatic.py) :
        transcription(directory)
        # E : on réactualise le chemin de traitement vers le dossier contenant les nouveaux ALTO4 :
        directory = "./temp_alto/"
    else:
        pass

# === 2. Création d'un fichier TEI ====
    # E : création des balises TEI (teiHeader, body) avec le paquet externe lxml et le module creationTEI.py :
    root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titlecat
    # E : on crée le teiHeader avec la fonction correspondante (module creationTEI.py) :
    teiHeader_xml = creation_header()
    # E : on l'ajoute à l'arborescence :
    root_xml.append(teiHeader_xml)
    # E : on créé les balises imbriquées text, body et list :
    text_xml = ET.SubElement(root_xml, "text")
    body_xml = ET.SubElement(text_xml, "body")
    list_xml = ET.SubElement(body_xml, "list")
    # E : on créé une liste vide avec laquelle on comptera les fichiers traités :
    n_fichier = 0

    # E : on créé une variable contenant l'arbre (elle sera utilisée à la fin pour écrire le teiHeader dans un fichier)
    xml_tree = ET.ElementTree(root_xml)

    # E : on appelle le dictionnaire de schémas souhaités présente sur contenu_TEI.py, et on boucle pour ajouter
    # leurs valeurs (des liens) en tant qu'instructions initiales de l'output :
    for schema in contenu_TEI.schemas.values():
        # l'instruction est traitée en tant que noeud :
        modele = ET.ProcessingInstruction('xml-model', schema)
        # le modèle est ajouté au dessus de la racine :
        xml_tree.getroot().addprevious(modele)
    # E : on appelle la feuille de style indiquée sur contenu_TEI.py et on la place dans une instruction initiale :
    if contenu_TEI.CSS != "":
        CSS = ET.ProcessingInstruction('xml-stylesheet', contenu_TEI.CSS)
        xml_tree.getroot().addprevious(CSS)

# === 3.1 Traitement préalable des ALTO en input ====
    # E : on traite chaque fichier ALTO (page transcrite du catalogue), en bouclant sur le dossier indiqué :
    # E : (la méthode os.listdir() renvoie une liste des fichiers contenus dans un dossier donné)
    for fichier in sorted(os.listdir(directory)):
        # E : exclusion des fichiers cachés (".[...]"). Cela rend le script fonctionnel sur mac (.DS_Store)
        # E : exclusion de fichiers autres que XML (permet la présence d'autres types de fichiers dans le dossier)
        if not fichier.startswith(".") and fichier.__contains__(".xml"):
            # E : on ajoute le ficher au comptage et on l'indique sur le terminal :
            n_fichier += 1
            print(str(n_fichier) + " – Traitement de " + fichier)
            # TODO commande -v retourne des erreurs
            # on contrôle la qualité du fichier ALTO si la commande -v est activée :
            if verifyalto:
                # E : on appelle les fonctions du module test_Validations_xml.py pour vérifier que le fichier ALTO est
                # bien formé et que la structure des entrées est respectée :
                # (le chemin est construit en associant le chemin vers le dossier + le nom du fichier actuel)
                print("\tVérification de la formation du fichier alto: ")
                check_strings(directory + fichier)
                print("\tVérification de la structure des entrées: ")
                get_entries(directory + fichier)
            else:
                pass
# === 3.2 Restructuration des ALTO en input ====
            # E : on appelle le module restructuration.py pour appliquer la feuille de transformation
            # Restructuration_alto.xsl aux fichiers en input et récupérer des fichiers avec les textlines en ordre :
            # (la fonction restructuration_automatique applique la feuille et retourne le chemin vers le fichier créé)
            chemin_restructuration = restructuration_automatique(directory, fichier)
            print('\tRestructuration du fichier effectuée (fichier "_restructuration.xml" créé)')
            # si le fichier en input contient "restructuration" dans son nom, on le compare a son output pour
            # détérminer s'il s'agit d'un fichier qui avait déjà été restructuré. Si c'est le cas, deux options :
            if fichier.__contains__("restructuration"):
                fichier_input = directory + fichier
                fichier_output = chemin_restructuration
                if open(fichier_input).read() == open(fichier_output).read():
                    print("\tATTENTION : ce fichier avait déjà été restructuré ; "
                      "le nouveau fichier produit est exactement pareil.")
                    # on demande sur le terminal si l'on souhaite le conserver
                    if input("Souhaitez vous le conserver ? [y/n]") == "n":
                        # si la réponse est non, on élimine le fichier restructuré en doublon :
                        print("--> Non. Le fichier original sera utilisé à sa place.")
                        os.remove(chemin_restructuration)
                        # si le dosser restructuration en résulte vide, on l'élimine :
                        if not os.listdir(directory + "restructuration"):
                            os.rmdir(directory + "restructuration/")
                        # le fichier original, déjà restructuré, est alors utilisé à la place du nouveau
                        chemin_restructuration = fichier_input
                    else:
                        print("--> Oui")
                        pass
                else:
                    pass

# === 4. Extraction des entrées ====
            # E : on indique le chemin vers le nouveau fichier restructuré et on le parse :
            document_alto = ET.parse(chemin_restructuration)
            # E : on appelle le module extractionCatEntrees.py pour extraire les données textuelles des ALTO restructurés :
            if n_fichier == 1:
                list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat,
                                                                        list_xml)
            else:
                list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat,
                                                                         list_xml, n_entree, n_oeuvre)
            # ajout des nouvelles entrées dans la balise list du fichier TEI :
            for entree in list_entrees:
                list_xml.append(entree)
            print("\t" + fichier + " traité")

    # si la valeur de l'output souhaité ne termine pas par ".xml", on le rajoute
    if not output.__contains__(".xml"):
        output = output + ".xml"
    # E : écriture du résultat de tout le processus de création TEI (arbre, entrées extraites) dans un fichier xml :
    xml_tree.write(output, pretty_print=True, encoding="UTF-8", xml_declaration=True)


# E : on lance la longue fonction définie précédemment et laquelle constitue ce script
# E : on vérifie que ce fichier est couramment exécuté (et non pas appelé sur un autre module)
# E : (quand on execute un script avec la commande "python3 run.py", sa valeur __name__ à la valeur de __main__)
if __name__ == "__main__":
    extraction()
