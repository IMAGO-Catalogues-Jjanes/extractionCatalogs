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
from extractionCatalogs.fonctions.restructuration import restructuration_automatique, correction_imbrication_segmentation
from extractionCatalogs.fonctions.Validations_xml import conformite_Segmonto, association_xml_rng
from extractionCatalogs.fonctions.XMLtoCSV import XML_to_CSV, csv_immediat
from extractionCatalogs.fonctions.automatisation_kraken.kraken_automatic import transcription
from extractionCatalogs.variables import contenu_TEI
from extractionCatalogs.fonctions.extractionCatEntrees_fonctions import ordonner_altos, nettoyer_liste_str_problemes


# === 1.2 Création des commandes pour lancer le script sur le Terminal ====
# commandes obligatoires :
@click.command()
@click.argument("directory", type=str)
@click.argument("output", type=str, required=False)
@click.argument("titlecat", type=str)
# options
@click.option("-st", "--segtrans", "segmentationtranscription", is_flag=True, default=False,
              help="Automatic segmentation and transcription via kraken. Input files must be images.")
#@click.option("-v", "--verify", "verifyalto", is_flag=True, default=False,
#              help="Verify ALTO4 input files conformity and structure")
# === 1.3 Création de la fonction principale du script ====
# la commande "python3 run.py" lance la fonction suivante, qui reprend les variables indiquées sur le terminal ;
# elle va elle-même faire appelle aux fonctions situées dans le dossier "fonctions"
def extraction(directory, output, titlecat, segmentationtranscription):
    """
    This python script takes a directory containing images or ALTO4 files of exhibition catalogs as an input. It's
    output is a directory containing an XML-TEI encoded version of the catalog, ALTO4 restructured files and a .txt file
    with information about eventual problems.

    directory: path to the directory containing images or ALTO4 files
    output: path to the directory where the extraction directory will be created
    titlecat: name for the processed catalog's TEI and ID ; ".xml" can be included but will be automatically generated.
    -st: take image files as an input instead of ALTO4. Automatic segmentation and transcription occurs via kraken.
    -v: verify ALTO4 files.
    """
    # === 1.1 Création d'un dossier pour les output   ====

    # si les chemins input ou output ne terminent pas par "/", le script ne tourne pas.
    # si ces "/" ne sont pas indiqués par l'utilisateur, on les ajoute pour éviter tout problème :
    if directory[-1] != "/":
        directory = directory + "/"
    if output[-1] != "/":
        output = output + "/"

    # on créé un switch pour vérifier si l'utilisateur souhaite uniquement produire un csv, sa valeur est "False" car normalement ce n'est pas le cas
    csv_direct = False
    # si le nom de l'output contient l'extension ".xml", on l'enlève (cela est nécessaire pour creer l'ID TEI ainsi que les dossiers d'extraction) :
    if titlecat.__contains__(".xml"):
        titlecat = titlecat[:-4]
    # si le nom de l'output contient l'extension ".csv", on l'enlève (cela est nécessaire pour creer les dossiers d'extraction) :
    elif titlecat.__contains__(".csv"):
        titlecat = titlecat[:-4]
        # mais on va aussi activer le switch csv_direct, afin d'indiquer à la pipeline qu'elle produise directement un fichier csv puis qu'elle s'arrêtte immédiatement
        csv_direct = True
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

    # === 2.2 Création directe d'un fichier csv, si la chaine "csv" est contenue dans le titre du catalogue  ====
    # si le titre du catalogue contient "csv", cela veut dire que l'utilisateur souhaite uniquement produire un fichier
    # csv à partir d'un fichier TEI déjà existant. Dans ce cas, la pipeline sera très courte, et consistera uniquement
    # dans la fonction "csv_immediat", qui appelle elle même la fonction XMLtoCSV
    if csv_direct == True:
        # on appelle la fonction :
        csv_immediat(titlecat, output_file, extraction_directory)
        # ON TERMINE LA PIPELINE :
        return
    # autrement : on continue avec toute la pipeline normale :
    else:
        pass
    # autrement : on continue avec toute la pipeline normale :

    # === 2.3 création du fichier problèmes et traitement de l'option -st  ====
    # On vérifie si un fichier correspondant "_problems.txt" existe déjà. Cela voudrait dire que la commande a déjà été
    # lancée auparavant, et on élimine ce fichier pour qu'un nouveau soit creé sans accumuler les informations en boucle
    problems = extraction_directory + "/" + titlecat + "_problems.txt"
    if os.path.exists(problems):
        os.remove(problems)

    # si l'on souhaite segmenter et océrriser automatiquement (-st) :
    # TODO : les commandes kraken ne semblent plus d'actualité ; vérifier fonction
    if segmentationtranscription:
        print("\tSegmentation et transcription automatiques en cours")
        # on appelle le module transcription (fichier kraken_automatic.py) :
        transcription(directory)
        # on réactualise le chemin de traitement vers le dossier contenant les nouveaux ALTO4 :
        directory = "./temp_alto/"
    else:
        pass



    # === 3. Création d'un arbre TEI ====
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

    # === 4.1 Traitement préalable des ALTO en input ====
    # la méthode os.listdir() renvoie une liste des fichiers contenus dans un dossier donné :
    liste_en_desordre = os.listdir(directory)
    # nous appelons la fonction ordonner_altos() dans extractionCatEntrees_fonctions.py, qui retourne une liste des
    # fichiers à traiter en ordre. Nous utilisons pas directement la méthode sorted() car celle-ci ordonne les fichiers
    # en tant que chaînes de caractères, ce qui brouille les numérotations si celles-ci n'utilisent pas de
    # "zéros non significatifs" (ex : "9" sera considéré plus grand que "10" s'il n'est pas nommé "09").
    liste_en_ordre = ordonner_altos(liste_en_desordre)

    # on créé une variable avec laquelle on comptera les fichiers traités :
    n_fichier = 0
    # on établit des variables qui nous permettront de faire des boucles :
    n_entree = 0
    n_oeuvre = 0
    # compteurs pour vérification ALTO : nombre de textlines mal situées dans le document en entrée
    textline_dans_main_total = 0
    textline_dans_autres_total = 0
    # compteur de problèmes d'ajout d'entryEnd et entry :
    entry_end_non_integrees = 0
    entry_non_integrees = 0
    # listes pour les problèmes à afficher dans problemes.txt :
    entryends_non_integrees_liste = []
    entries_non_integrees_liste = []
    problemes_Segmonto_total = []
    # Liste pour ajouter des lignes mises de côté lors de la correction de l'imbrication des TextBlock mal saisis sur eScriptorium
    TextLine_dans_Mainzone_liste_total = []
    # on traite chaque fichier ALTO (page transcrite du catalogue), en bouclant sur le dossier indiqué :
    for fichier in liste_en_ordre:
        # on établit un compteur pour afficher sur le terminal le numéro d'étape dans le traitement du fichier :
        etape = 0
        # exclusion des fichiers cachés (".[...]"). Cela rend le script fonctionnel sur mac (.DS_Store)
        # exclusion de fichiers autres que XML (permet la présence d'autres types de fichiers dans le dossier)
        if not fichier.startswith(".") and fichier.__contains__(".xml"):
            # on ajoute le ficher au comptage et on l'indique sur le terminal :
            n_fichier += 1
            # on construit pour chaque fichier un message précédé par une barre de signes "=" afin que le message sur le terminal soit visuellement clair
            message = str(n_fichier) + " – Traitement de " + fichier
            barre = ""
            # on boucle sur le nombre de caracteres du message, afin que la barre soit adaptée à sa taille
            for caractere in message:
                barre += "="
            print("\n")
            print(barre)
            print(message)

            # === 4.2 On analyse la conformité et la structure des fichiers ALTO ====
            # on appelle les fonctions du module Validations_xml.py
            # (le chemin est construit en associant le chemin vers le dossier + le nom du fichier actuel)
            etape += 1
            print("\t" + str(etape) + " – Vérification de la conformité à l'ontologie Segmonto")

            # on récupère des compteurs et une liste relatifs aux problèmes de conformité avec l'ontologie Segmonto dans Validations_xml.py
            textline_dans_main, textline_dans_autres, problemes_Segmonto = conformite_Segmonto(directory + fichier)#

            # on ajoute la liste à une liste contenant les problèmes de tous les fichiers :
            if problemes_Segmonto:
                problemes_Segmonto_total.append(problemes_Segmonto)
            else:
                print("\t   ✓ le fichier issu d'eScriptorium est conforme à l'ontologie Segmonto")

            # on rajoute ces chiffres produits à chaque itération à des listes définies préalablement :
            textline_dans_main_total += textline_dans_main
            textline_dans_autres_total += textline_dans_autres
            # ces listes seront appelées à la fin du script pour montrer des messages sur le terminal

            # === 4.3 Restructuration des ALTO en input ====
            etape += 1
            print('\t{} – Restructuration du fichier'.format(etape))
            # on appelle le module restructuration.py pour appliquer la feuille de transformation
            # Restructuration_alto.xsl aux fichiers en input et récupérer des fichiers avec les textLines en ordre :
            # (la fonction restructuration_automatique applique la feuille et retourne le chemin vers le fichier créé)
            chemin_restructuration = restructuration_automatique(directory, fichier, extraction_directory)
            # si le fichier en input contient "restructuration" dans son nom, on le compare a son output pour
            # détérminer s'il s'agit d'un fichier qui avait déjà été restructuré. Si c'est le cas, deux options :
            if fichier.__contains__("restructuration"):
                fichier_input = directory + fichier
                fichier_output = chemin_restructuration
                if open(fichier_input).read() == open(fichier_output).read():
                    print("\n\t[!] ATTENTION : ce fichier avait déjà été restructuré ; "
                          "le nouveau fichier produit est identique.")
                    # on demande sur le terminal si l'on souhaite l'éliminer :
                    if input("\tSouhaitez vous l'éliminer et utiliser l'original à la place ? [y/n]") == "n":
                        print("\t--> Non. Le nouveau fichier restructuré sera utilisé.")
                    else:
                        # si la réponse est oui, on élimine le fichier restructuré en doublon :
                        print("\t--> Oui. Le fichier original sera utilisé à la place.\n")
                        os.remove(chemin_restructuration)
                        # si le dosser restructuration en résulte vide, on l'élimine :
                        if not os.listdir(os.path.dirname(chemin_restructuration)):
                            os.rmdir(os.path.dirname(chemin_restructuration))
                        # le fichier original, déjà restructuré, est alors utilisé à la place du nouveau
                        chemin_restructuration = fichier_input
                else:
                    pass
            if chemin_restructuration:
                print("\t   ✓ fichier '{}_restructuration.xml' créé".format(fichier))

            # === 4.4 restructuration eventuelle de la segmentation des ALTO en input ====
            # On appelle une fonction qui vérifie que l'imbrication des éléments du fichier ALTO est correcte.
            # Si ce n'est pas le cas, la fonction corrige les problèmes
            etape += 1
            print("\t" + str(etape) + " – Vérification de l'imbrication des zones saisies sur eScriptorium ")
            chemin_resegmentation, TextLine_dans_Mainzone_liste = correction_imbrication_segmentation(chemin_restructuration)
            # S'il y a eu une correction, on actualise le chemin de traitement vers un nouveau fichier produit :
            if chemin_resegmentation:
                chemin_restructuration = chemin_resegmentation
            if TextLine_dans_Mainzone_liste:
                TextLine_dans_Mainzone_liste_total.append(TextLine_dans_Mainzone_liste)

            # === 5. Extraction des entrées ====
            etape += 1
            print("\t" + str(etape) + " – Extraction :")
            print("\n")
            # on indique le chemin vers le nouveau fichier restructuré et on le parse :
            document_alto = ET.parse(chemin_restructuration)
            # on appelle le module extractionCatEntrees.py pour extraire les données textuelles des ALTO restructurés :
            list_xml, list_entrees, n_entree, n_oeuvre, entryend_non_integree, entry_non_integree, entryend_non_integree_liste, entry_non_integree_liste = \
                extInfo_Cat(document_alto, titlecat, list_xml, n_entree, n_oeuvre)

            # si l'entrée courante n'est pas aoutée au TEI, on l'ajoute à la liste d'objets non intégrées
            if entryend_non_integree_liste:
                entryends_non_integrees_liste.append(entryend_non_integree_liste)
            if entry_non_integree_liste:
                entries_non_integrees_liste.append(entry_non_integree_liste)
            # si le return indique que lors de l'itération courante une entryend n'a pas été ingégrée, on augmente un compteur dédié :
            if entryend_non_integree == True:
                entry_end_non_integrees += 1
            if entry_non_integree == True:
                entry_non_integrees += 1
            # ajout des nouvelles entrées dans la balise list du fichier TEI :
            for entree in list_entrees:
                list_xml.append(entree)

    # === 6. Outputs : TEI et CSV ====

    # on ajoute ou on redonne au nom du catalogue la terminaison en ".xml"
    if not output_file.__contains__(".xml"):
        output_file = output_file + ".xml"
    # afin que notre fichier csv soit conforme, on va remplacer les ";" dans le texte par des "," : ainsi, le séparateur ";" traitera correctement le fichier:
    texte = xml_tree.xpath('//text()')
    for node in texte:
        if ";" in node:
            print(node)
            balise = node.getparent()
            node = node.replace(";", ",")
            balise.text = node
    # afin que notre fichier csv soit conforme, on va remplacer les '"' dans le texte par des "'" : ainsi, le séparateur ";" traitera correctement le fichier:

    for node in texte:
        if '"' in node:
            balise = node.getparent()
            node = node.replace('"', "'")
            balise.text = node

    # Avant d'écrire le résultat dans un fichier TEI, on va vérifier s'il n'y a pas déjà un fichier avec le même nom :
    if os.path.exists(output_file):
        # s'il y en a un, on va écrire un fichier avec le résultat de la pipeline juste pour le comparer à ce fichier
        # antérieur. Le fichier de vérification sera ensuite éliminé :
        verification_file = output_file.replace(".xml", "_verification.xml")
        xml_tree.write(verification_file, pretty_print=True, encoding="UTF-8", xml_declaration=True)
        fichier_anterieur = output_file
        # si les deux fichiers ont le même contenu :
        if open(fichier_anterieur).read() == open(verification_file).read():
            os.remove(verification_file)
            # cela veut dire qu'il n'y a pas danger de perte de données, on continue la pipeline :
            pass
        # s'ils différent, il est possible que l'utilisateur perdent des données corrigées !
        # soit le fichier TEI Ancien avait été corrigé manuellement
        # soit ce sont les fichiers en input qui ont été corrigés et qui produisent donc un fichier TEI différent de l'ancien
        # c'est à l'utilisateur de choisir lequel des deux fichiers il veut conserver :
        else:
            print("\n========================================================================================================================="
                  "\n[!] ATTENTION : un fichier TEI avec le même nom de catalogue a déjà été produit et diffère dans son contenu; "
                  "\nSoit ce fichier a été MODIFIÉ/CORRIGÉ MANUELLEMENT, soit les fichiers ALTO en input ont été MODIFIÉS/CORRIGÉS MANUELLEMENT.")
            # on demande sur le terminal si l'on souhaite l'éliminer :
            if input("\tSouhaitez vous que le fichier TEI ancien soit remplacé ? [y/n]\n") == "n":
                os.remove(verification_file)
                print("\t--> Le dossier d'extraction n'a pas été modifié. Aucun résultat de la pipeline n'a été enregistré.")
                return
            else:
                os.remove(verification_file)
                print("\t--> Oui. Le fichier antérieur sera remplacé.\n")

    # écriture du résultat de tout le processus de création TEI (arbre, entrées extraites) dans un fichier xml :
    xml_tree.write(output_file, pretty_print=True, encoding="UTF-8", xml_declaration=True)
    # on créé le fichier CSV
    csv_produit = XML_to_CSV(output_file, extraction_directory, titlecat)

    # === 7. Informations à afficher sur le terminal ====
    print("\n")
    print(barre)
    print("    Résumé :")

    # nombre de fichiers :
    if n_fichier == 1:
        print("\t{} page de catalogue traitée [fichier ALTO]".format(n_fichier))
    else:
        print("\t{} pages de catalogue traitées [fichiers ALTO]".format(n_fichier))

    # nombre total d'entrées extraites dans les fichiers ALTO :
    entrees = xml_tree.find(".//list")
    n_entrees = 0
    for entree in entrees:
        n_entrees +=1
    if n_entrees == 1:
        print("\t{} entrée de catalogue extraite [TextBlock 'CustomZone:entry']".format(n_entrees))
    else:
        print("\t{} entrées de catalogue extraites [TextBlocks 'CustomZone:entry']".format(n_entrees))

    # balises name vides (exposants non signalés)
    exposant_vide = xml_tree.xpath(".//list//name[not(node())]")
    vides = 0
    liste_vides = []
    for vide in exposant_vide:
        vides += 1
        # on indique dans une liste les entrées concernées
        liste_vides.append(vide.xpath("./../../@n"))
    # on nettoie le résultat :
    str_vides = str(liste_vides)
    str_vides = str_vides.replace("[", "").replace("]", "")

    # nombre d'exposants signalés et non signalés exposant
    exposants = xml_tree.xpath(".//list//name/text()")
    n_exposants = 0
    for exposant in exposants:
        n_exposants += 1
    # si le nombre d'exposants correspond aux entrées, il n'y a pas d'exposants non signalés :
    if n_exposants == n_entrees:
        if n_exposants == 1:
            print("\t{} exposant signalé".format(n_exposants))
        else:
            print("\t{} exposants signalés".format(n_exposants))
    # autrement, on signale combien d'exposants n'ont pas été signalés et quelles sont les entrées concernées :
    else:
        # nous accordons la phrase au singulier ou au pluriel selon les cas possibles :
        if n_exposants == 1 and vides == 1:
            print("\t{} exposant signalé, {} exposant non signalé"
                   " (entrée nº : {}) ".format(n_exposants, vides, str_vides))
        elif n_exposants == 1 and vides > 1:
            print("\t{} exposant signalé, {} exposants non signalés"
                  " (entrée nº : {}) ".format(n_exposants, vides, str_vides))
        elif n_exposants > 1 and vides == 1:
            print("\t{} exposants signalés, {} exposant non signalé"
                   " (entrée nº : {}) ".format(n_exposants, vides, str_vides))
        elif n_exposants > 1 and vides > 1:
            print("\t{} exposants signalés, {} exposants non signalés"
                  " (entrées nº : {}) ".format(n_exposants, vides, str_vides))

    # nombre d'oeuvres
    oeuvres = xml_tree.findall(".//item")
    n_items = 0
    for oeuvre in oeuvres:
        n_items += 1
    if n_oeuvre == 1:
        print("\t{} oeuvre extraite".format(n_items))
    else:
        print("\t{} oeuvres extraites".format(n_items))

    # avertissement si aucune entrée n'a été extraite
    if n_entrees == 0:
        print("\n[!] ATTENTION : Aucune entrée n'a été extraite des fichiers restructurés ; veuillez vérifier les "
              "regex utilisées pour l'extraction ou la structure des fichiers ALTO en input")
    else:
        pass

    # messages relatif à la la vérification ALTO :
    # s'il y a des chiffres à signaler :
    print("\n    Analyse des fichiers en input [ALTO] :")

    if TextLine_dans_Mainzone_liste_total :
        lignes_chiffre = 0
        for lines in TextLine_dans_Mainzone_liste_total:
            for line in lines:
                lignes_chiffre +=1
        if lignes_chiffre == 1:
            print("\t[!] {} ligne non traitée fait potentiellement partie des entrées du catalogue. Elle a été ajoutée au fichier {}_problems.txt".format(lignes_chiffre, titlecat))
        else:
            print("\t[!] {} lignes non traitées font potentiellement partie des entrées du catalogue. Elles ont été ajoutées au fichier {}_problems.txt".format(lignes_chiffre, titlecat))

    n_fichiers_problemes_alto = 0
    for fichier in problemes_Segmonto_total:
        n_fichiers_problemes_alto +=1
    if n_fichiers_problemes_alto == 0 :
        print("\t✓ La segmentation des pages est conforme à l'ontologie Segmonto")
    elif n_fichiers_problemes_alto == 1:
        print("\t[!] {} fichier non conforme à l'ontologie Segmonto. Consulter le fichier {}_problemes.text.".format(
                len(problemes_Segmonto_total), titlecat))
    else:
        print("\t[!] {} fichiers non conformes à l'ontologie Segmonto. Consulter le fichier {}_problemes.text.".format(
            len(problemes_Segmonto_total), titlecat))

    # messages pour le TEI produit
    print("    Analyse du fichier en output [TEI] :")
    association_xml_rng(output_file)
    # message si des entry n'ont pas été intégrées :
    if entry_non_integrees >= 1:
        if entry_non_integrees == 1:
            print("\t[!] {} entrée de catalogue [TextBlock 'CustomZone:entry'] n'a pas été intégrée au fichier TEI. Elle a été ajoutée au fichier {}_problems.txt".format(
                entry_non_integrees, titlecat)
            )
        else:
            print("\t[!] {} entrées de catalogue [TextBlock 'CustomZone:entry'] n'ont pas été intégrées au fichier TEI. Elles ont été ajoutées au fichier {}_problems.txt".format(
                entry_non_integrees, titlecat)
            )
    # message si des entryend n'ont pas été intégrées :
    if entry_end_non_integrees >= 1:
        if entry_end_non_integrees == 1:
            print("\t[!] {} fin d'entrée de catalogue [TextBlock 'CustomZone:entryEnd'] n'a pas été intégrée au fichier TEI. Elle a été ajoutée au fichier {}_problems.txt".format(
                entry_end_non_integrees, titlecat)
            )
        else:
            print("\t[!] {} fins d'entrée de catalogue [TextBlock 'CustomZone:entryEnd'] n'ont pas été intégrées au fichier TEI. Elles ont été ajoutées au fichier {}_problems.txt".format(
                entry_end_non_integrees, titlecat)
            )

    print("    Création d'un tableur csv :")
    if csv_produit == True:
        print("\t ✓ Le fichier csv a été produit")
    elif csv_produit == False:
        print("\t[!] Le fichier csv n'a pas été produit. Vérifiez la conformité du fichier TEI.")

    # le terminal indique à la fin le chemin absolu vers le dossier d'extraction
    chemin_absolu = os.path.abspath(extraction_directory)
    print("\n    Chemin du dossier d'extraction : {}\n".format(chemin_absolu))

    # === 5. Informations à mettre sur le fichier problemes.txt ====
    if str_vides:
        with open(os.path.dirname(output_file) + "/" + titlecat + "_problems.txt", mode="a") as f:
            f.write("\n")
            f.write("––––––––––––––––––––––––––––––––––––––––––––")
            f.write("\nexposants non signalés : ")
            for exposant in liste_vides:
                f.write("\n – entrée " + nettoyer_liste_str_problemes(str(exposant).replace("'", "").replace('"', '')))
            f.write("\n")

    if entries_non_integrees_liste:
        with open(os.path.dirname(output_file) + "/" + titlecat + "_problems.txt", mode="a") as f:
            f.write("\n")
            f.write("––––––––––––––––––––––––––––––––––––––––––––")
            f.write("\nObjets 'entry' avec items non ajoutés au fichier TEI : ")
            for chaine in entries_non_integrees_liste:
                f.write("\n – " + nettoyer_liste_str_problemes(str(chaine)))
            f.write("\n")

    if entryends_non_integrees_liste:
        with open(os.path.dirname(output_file) + "/" + titlecat + "_problems.txt", mode="a") as f:
            f.write("\n")
            f.write("––––––––––––––––––––––––––––––––––––––––––––––")
            f.write("\nObjets 'entryEnd' non ajoutés au fichier TEI : ")
            for chaine in entryends_non_integrees_liste:
                f.write("\n – " + nettoyer_liste_str_problemes(str(chaine)))
            f.write("\n")

    if TextLine_dans_Mainzone_liste_total:
        with open(os.path.dirname(output_file) + "/" + titlecat + "_problems.txt", mode="a") as f:
            f.write("\n")
            f.write("––––––––––––––––––––––––––––––––––––––––––––––")
            f.write("\nObjets 'TextLine' pouvant constituer des lignes de catalogue non ajoutées au fichier TEI ")
            for lines in TextLine_dans_Mainzone_liste_total:
                for line in lines:
                    line = "\n – " + line
                    f.write(line)
            f.write("\n")

    if problemes_Segmonto_total:
        with open(os.path.dirname(output_file) + "/" + titlecat + "_problems.txt", mode="a") as f:
            f.write("\n")
            f.write("––––––––––––––––––––––––––––––––––––––––––––––")
            f.write("\nFichiers ALTO en input :")
            for problemes in problemes_Segmonto_total:
                for probleme in problemes:
                    line = "\n– " + probleme.replace("[!]", "").replace("\t   ", "").replace("\n", "")
                    f.write(line)
            f.write("\n")
    # on récupère les descriptions vides pour enlever les balises :

# on lance la fonction définie précédemment et qui constitue la totalité du fichier
# on vérifie que ce fichier est couramment exécuté (et non pas appelé sur un autre module)
# (quand on execute un script avec la commande "python3 run.py", sa valeur __name__ à la valeur de __main__)
if __name__ == "__main__":
    extraction()
