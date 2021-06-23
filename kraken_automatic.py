import subprocess
import os

chemin = input("Entrez le chemin du dossier contenant les images à océsirer: ")
dossier_resultat = input("Entrez le chemin du dossier résultat : ")

for fichier in os.listdir(chemin):
    bash_command = 'kraken -i ' + chemin + fichier + ' ' + dossier_resultat + fichier[:-3]+\
                   'xml -a segment -bl -i segmentationv3.mlmodel ocr -m model_best_100.mlmodel '
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(fichier + 'done')
