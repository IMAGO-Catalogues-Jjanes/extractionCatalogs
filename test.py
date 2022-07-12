import os
from run import extraction

path = "./tests_Esteban_input/"
input_dir = os.listdir("./tests_Esteban_input/")
output_dir = "./tests_Esteban_output/"

for cat in input_dir:
    path2 = path + cat
    extraction(path2, output_dir, cat)
    path2 = ""
