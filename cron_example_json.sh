#!/usr/bin/bash

source /home/rdas/.bashrc_conda
conda activate machinelearning_gpu
python3 /data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/generate_json.py
conda deactivate
