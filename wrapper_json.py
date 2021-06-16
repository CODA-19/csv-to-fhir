#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess, os
 

"""

Created on Sat May  1 01:55:22 2021


This script uses subprocess calls in a sequence to execute the different
csv-json scripts.

It first defines a list and then using the list index pass the latter as an
argument for the Python subprocess.



@author: rdas

"""

pathOfscripts = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping'

file_list = ['demo_csv-json.py','epi_csv-json.py','diagnosis_csv-json.py','drug_csv-json.py','culture_csv-json.py','pcr_csv-json.py','observation_csv-json.py','lab_csv-json.py']




print(os.path.join(pathOfscripts, file_list[0]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[0])], shell=True)

print(os.path.join(pathOfscripts, file_list[1]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[1])], shell=True)

print(os.path.join(pathOfscripts, file_list[2]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[2])], shell=True)

print(os.path.join(pathOfscripts, file_list[3]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[3])], shell=True)

print(os.path.join(pathOfscripts, file_list[4]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[4])], shell=True)

print(os.path.join(pathOfscripts, file_list[5]))

subprocess.call(['python ' + os.path.join(pathOfscripts,file_list[5])], shell=True)
    





