"""
Cette fonction est appelée avec la commande optionnelle "-st"
Elle n'est pas fonctionnelle en l'État ; il faudrait l'adapter aux évolutions de kraken
"""

import subprocess
import os


def transcription(chemin):
    """
    Pour un dossier donné, on lance kraken sur toutes les images contenues.
    :param chemin: chemin vers le dossier contenant les images à océsirer.
    :type chemin: str
    :return:
    """
    for fichier in os.listdir(chemin):
        # on exclue les éventuels fichiers XML du dossier ainsi que les fichiers/dossiers cachés (.DS_Store sur mac)
        if not fichier.__contains__(".xml") and not fichier.startswith("."):
            bash_command = 'kraken -i ' + chemin + fichier + ' ' + "./temp_alto/" + fichier[:-3] + \
                           'xml -a segment -bl -i segmentationv3.mlmodel ocr -m model_best_100.mlmodel'
            process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
            output, error = process.communicate()
            print(fichier + 'done')
