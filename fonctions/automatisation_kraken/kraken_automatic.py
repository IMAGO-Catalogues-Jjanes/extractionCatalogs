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
        bash_command = 'kraken -i ' + chemin + fichier + ' ' + "./temp_alto/" + fichier[:-3] + \
                       'xml -a segment -bl -i segmentationv3.mlmodel ocr -m model_best_100.mlmodel'
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print(fichier + 'done')

