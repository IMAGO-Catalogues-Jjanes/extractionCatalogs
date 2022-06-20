"""
Initialisation du programme
Programme permettant, à partir de catalogues d'expositions océrisés avec Kraken, d'extraire les données contenues
dans le fichier de sortie de l'OCR (ALTO4 XML), et de construire un fichier TEI sur le modèle de l'ODD défini par
Caroline Corbières (https://github.com/carolinecorbieres/ArtlasCatalogues/blob/master/5_ImproveGROBIDoutput/ODD/ODD_Transformation.xml)

Le programme est particulièrement adapté à un traitement à partir d'eScriptorium, une interface pour kraken permettant de visualiser
le processus de segmentation puis d'obtenir les fichier ALTO4 nécessaires à cette pipeline.

Author:
Juliette Janès, 2021
Esteban Sánchez Oeconomo, 2022
"""

# === 1.1 On appelle les paquets externes, modules et fonctions nécessaires ====
# paquets externes
from lxml import etree as ET
import os
import click
# modules du script
from extractionCatalogs.fonctions.extractionCatEntrees import extInfo_Cat
from extractionCatalogs.fonctions.creationTEI import creation_header
from extractionCatalogs.fonctions.restructuration import restructuration_automatique
from extractionCatalogs.fonctions.validation_alto.test_Validations_xml import check_strings, get_entries
from extractionCatalogs.fonctions.automatisation_kraken.kraken_automatic import transcription
from extractionCatalogs.variables import contenu_TEI
from extractionCatalogs.fonctions.extractionCatEntrees_fonctions import ordonner_altos


# === 1.2 Création des commandes pour lancer le script sur le Terminal ====
# commandes obligatoires :
@click.command()
@click.argument("directory", type=str)
@click.argument("output", type=str, required=False)
@click.argument("titlecat", type=str)
@click.argument("typecat", type=click.Choice(['Nulle', "Simple", "Double", "Triple"]), required=True)
# options
@click.option("-st", "--segtrans", "segmentationtranscription", is_flag=True, default=False,
              help="Automatic segmentation and transcription via kraken. Input files must be images.")
@click.option("-v", "--verify", "verifyalto", is_flag=True, default=False,
              help="Verify ALTO4 input files conformity and structure")
# === 1.3 Création de la fonction principale du script ====
# la commande "python3 run.py" lance la fonction suivante, qui reprend les variables indiquées sur le terminal ;
# elle va elle-même faire appelle aux fonctions situées dans le dossier "fonctions"
def extraction(directory, output, titlecat, typecat, verifyalto, segmentationtranscription):
    """
    This python script takes a directory containing images or ALTO4 files of exhibition catalogs as an input. It's
    output is a directory containing an XML-TEI encoded version of the catalog, ALTO4 restructured files and a .txt file
    with information about eventual problems.

    directory: path to the directory containing images or ALTO4 files
    output: path to the directory where the extraction directory will be created
    titlecat: name for the processed catalog's TEI and ID ; ".xml" can be included but will be automatically generated.
    typeCat: catalog's type according to the division presented in the github of the project (Nulle, Simple, Double or Triple)
    -st: take image files as an input instead of ALTO4. Automatic segmentation and transcription occurs via kraken.
    -v: verify ALTO4 files.
    """

    # === 1.4 Création d'un dossier pour les output et traitement des options activées ====

    # si le nom de l'output contient l'extension ".xml", on l'enlève (cela est nécessaire pour creer l'ID TEI) :
    if titlecat.__contains__(".xml"):
        titlecat = titlecat[:-4]
    else:
        pass

    # On créé un dossier pour les output (TEI, fichier de problèmes, dossier restructuration) :
    # on construit un chemin vers le dossier d'extraction en récupérant le chemin output :
    extraction_directory = output + "extraction_" + titlecat
    # Si le chemin n'existe pas, on créé le dossier (s'il existait, on aurait une erreur) :
    if not os.path.exists(extraction_directory):
        #  la méthode makedirs permet de créer tous les dossiers du chemin (mkdir est limité à un seul dossier)
        os.makedirs(extraction_directory)
    # on assigne à une variable le chemin vers le fichier
    output_file = extraction_directory + "/" + titlecat

    # On vérifie si un fichier correspondant "_problems.txt" existe déjà. Cela voudrait dire que la commande a déjà été
    # lancée auparavant, et on élimine ce fichier pour qu'un nouveau soit creé sans accumuler les informations en boucle
    problems = extraction_directory + "/" + titlecat + "_problems.txt"
    if os.path.exists(problems):
        os.remove(problems)

    # si l'on souhaite segmenter et océrriser automatiquement (-st) :
    # TODO : les commandes kraken ne semblent plus d'actualité ; vérifier fonction
    if segmentationtranscription:
        print("Segmentation et transcription automatiques en cours")
        # on appelle le module transcription (fichier kraken_automatic.py) :
        transcription(directory)
        # on réactualise le chemin de traitement vers le dossier contenant les nouveaux ALTO4 :
        directory = "./temp_alto/"
    else:
        pass

    # === 2. Création d'un fichier TEI ====
    # création des balises TEI (teiHeader, body) avec le paquet externe lxml et le module creationTEI.py :
    root_xml = ET.Element("TEI", xmlns="http://www.tei-c.org/ns/1.0")
    root_xml.attrib["{http://www.w3.org/XML/1998/namespace}id"] = titlecat
    # on crée le teiHeader avec la fonction correspondante (module creationTEI.py) :
    teiHeader_xml = creation_header()
    # on l'ajoute à l'arborescence :
    root_xml.append(teiHeader_xml)
    # on créé les balises imbriquées text, body et list :
    text_xml = ET.SubElement(root_xml, "text")
    body_xml = ET.SubElement(text_xml, "body")
    list_xml = ET.SubElement(body_xml, "list")
    # on créé une liste vide avec laquelle on comptera les fichiers traités :
    n_fichier = 0

    # on créé une variable contenant l'arbre (elle sera utilisée à la fin pour écrire le teiHeader dans un fichier)
    xml_tree = ET.ElementTree(root_xml)

    # on appelle le dictionnaire de schémas souhaités présente sur contenu_TEI.py, et on boucle pour ajouter
    # leurs valeurs (des liens) en tant qu'instructions initiales de l'output :
    for schema in contenu_TEI.schemas.values():
        # l'instruction est traitée en tant que noeud :
        modele = ET.ProcessingInstruction('xml-model', schema)
        # le modèle est ajouté au dessus de la racine :
        xml_tree.getroot().addprevious(modele)
    # on appelle la feuille de style indiquée sur contenu_TEI.py et on la place dans une instruction initiale :
    if contenu_TEI.CSS != "":
        CSS = ET.ProcessingInstruction('xml-stylesheet', contenu_TEI.CSS)
        xml_tree.getroot().addprevious(CSS)

    # === 3.1 Traitement préalable des ALTO en input ====
    # la méthode os.listdir() renvoie une liste des fichiers contenus dans un dossier donné :
    liste_en_desordre = os.listdir(directory)
    # nous appelons la fonction ordonner_altos() dans extractionCatEntrees_fonctions.py, qui retourne une liste des
    # fichiers à traiter en ordre. Nous utilisons pas directement la méthode sorted() car celle-ci ordonne les fichiers
    # en tant que chaînes de caractères, ce qui brouille les numérotations si celles-ci n'utilisent pas de
    # "zéros non significatifs" (ex : "9" sera considéré plus grand que "10" s'il n'est pas nommé "09").
    liste_en_ordre = ordonner_altos(liste_en_desordre)

    # on traite chaque fichier ALTO (page transcrite du catalogue), en bouclant sur le dossier indiqué :
    for fichier in liste_en_ordre:
        # exclusion des fichiers cachés (".[...]"). Cela rend le script fonctionnel sur mac (.DS_Store)
        # exclusion de fichiers autres que XML (permet la présence d'autres types de fichiers dans le dossier)
        if not fichier.startswith(".") and fichier.__contains__(".xml"):
            # on ajoute le ficher au comptage et on l'indique sur le terminal :
            n_fichier += 1
            print(str(n_fichier) + " – Traitement de " + fichier)
            # TODO commande -v retourne des erreurs
            # on contrôle la qualité du fichier ALTO si la commande -v est activée :
            if verifyalto:
                # on appelle les fonctions du module test_Validations_xml.py pour vérifier que le fichier ALTO est
                # bien formé et que la structure des entrées est respectée :
                # (le chemin est construit en associant le chemin vers le dossier + le nom du fichier actuel)
                print("\tVérification de la formation du fichier alto: ")
                check_strings(directory + fichier)
                print("\tVérification de la structure des entrées: ")
                get_entries(directory + fichier)
            else:
                pass
            # === 3.2 Restructuration des ALTO en input ====
            # on appelle le module restructuration.py pour appliquer la feuille de transformation
            # Restructuration_alto.xsl aux fichiers en input et récupérer des fichiers avec les textLines en ordre :
            # (la fonction restructuration_automatique applique la feuille et retourne le chemin vers le fichier créé)
            chemin_restructuration = restructuration_automatique(directory, fichier, extraction_directory)
            print('\tRestructuration du fichier effectuée (fichier "_restructuration.xml" créé)')
            # si le fichier en input contient "restructuration" dans son nom, on le compare a son output pour
            # détérminer s'il s'agit d'un fichier qui avait déjà été restructuré. Si c'est le cas, deux options :
            if fichier.__contains__("restructuration"):
                fichier_input = directory + fichier
                fichier_output = chemin_restructuration
                if open(fichier_input).read() == open(fichier_output).read():
                    print("\tATTENTION : ce fichier avait déjà été restructuré ; "
                          "le nouveau fichier produit est identique.")
                    # on demande sur le terminal si l'on souhaite l'éliminer :
                    if input("Souhaitez vous l'éliminer et utiliser l'original à la place ? [y/n]") == "n":
                        print("--> Non. Le nouveau fichier restructuré sera utilisé.")
                    else:
                        # si la réponse est oui, on élimine le fichier restructuré en doublon :
                        print("--> Oui. Le fichier original sera utilisé à la place.")
                        os.remove(chemin_restructuration)
                        # si le dosser restructuration en résulte vide, on l'élimine :
                        if not os.listdir(os.path.dirname(chemin_restructuration)):
                            os.rmdir(os.path.dirname(chemin_restructuration))
                        # le fichier original, déjà restructuré, est alors utilisé à la place du nouveau
                        chemin_restructuration = fichier_input
                else:
                    pass

            # === 4. Extraction des entrées ====
            # on indique le chemin vers le nouveau fichier restructuré et on le parse :
            document_alto = ET.parse(chemin_restructuration)
            # on appelle le module extractionCatEntrees.py pour extraire les données textuelles des ALTO restructurés :
            if n_fichier == 1:
                list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat, output_file,
                                                                         list_xml)
            else:
                list_xml, list_entrees, n_entree, n_oeuvre = extInfo_Cat(document_alto, typecat, titlecat, output_file,
                                                                         list_xml, n_entree, n_oeuvre)
            # ajout des nouvelles entrées dans la balise list du fichier TEI :
            for entree in list_entrees:
                list_xml.append(entree)
            print("\t" + fichier + " traité")

    # on ajoute ou on redonne au nom du catalogue la terminaison en ".xml"
    if not output_file.__contains__(".xml"):
        output_file = output_file + ".xml"
    # écriture du résultat de tout le processus de création TEI (arbre, entrées extraites) dans un fichier xml :
    xml_tree.write(output_file, pretty_print=True, encoding="UTF-8", xml_declaration=True)

    # nous indiquons dans le terminal le nombre total d'entrée extraites dans les fichiers ALTO restructurés :
    entrees = xml_tree.find(".//list")
    n_entrees = 0
    for entree in entrees:
        n_entrees +=1
    if n_entrees > 1:
        print("\n{} entrées ont été extraites de l'ensemble des fichiers restructurés".format(n_entrees))
    elif n_entrees == 1:
        print("\n{} entrée a été extraite de l'ensemble des fichiers restructurés".format(n_entrees))
    # Si aucune entrée n'est extraite dans l'ensemble de fichiers, possible erreur d'instanciation regex :

    elif n_entrees == 0:
                print("\nATTENTION : Aucune entrée n'a été extraite des fichiers restructurés ; veuillez vérifier vos instanciations"
              " d'extraction regex")

    # le terminal indique à la fin le chemin absolu vers le dossier d'extraction
    print("\nChemin du dossier d'extraction : {}".format(os.path.abspath(extraction_directory)))


# on lance la longue fonction définie précédemment et laquelle constitue ce script
# on vérifie que ce fichier est couramment exécuté (et non pas appelé sur un autre module)
# (quand on execute un script avec la commande "python3 run.py", sa valeur __name__ à la valeur de __main__)
if __name__ == "__main__":
    extraction()
