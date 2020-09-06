#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 03:05:25 2020


This program reads the relevant csv files and then creates
a json file using the data retrieved based on the FHIR
structure.


@author: rdas
"""

import numpy as np
import pandas as pd
import json as js
import csv as cv


## Define the paths (The paths here are those that considered the CITADEL infrastructure)

pathOfDrugfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/drug_data.csv'
pathofDrugJsonfile = '/data8/network_mount/S/FHIR_json/drug_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfDrug = pd.read_csv(pathOfDrugfile)



def drug_dic_json(dfDrug):
    
      
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfDrug type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    
    for i in range(len(dfDrug)):
        
        
        single_json = {
                  
                  

                  # The type of resource                    
                  
                  "resourceType": "MedicationAdministration",
                  
                  # Each resource entry needs a unique id for the ndjson bulk upload. 
                  
                  "id": "Provide id here",
                  
                  "subject": {
                    
                          "reference": "Patient/pat1"
                    
                  },
                  

                  "contained": [
                    {
                      "resourceType": "Medication",
                      "id": "med0301",
                      "code": {
                        "coding": [
                          {
                            "system": "http://hl7.org/fhir/sid/ndc",
                            "code": "0069-2587-10",
                            "display": dfDrug.iloc[i]["drug_name"]
                          }
                        ]
                      }
                    },
                    
                  ],
                  

                  
                  "effectivePeriod": {
                     # YYYY-MM-DDThh:mm:ss+zz:zz
                     "start": "2017-02-01T17:23:07Z",
                     "end": "2017-03-01T17:23:07Z"
                 },
                  
                  
                 "dosage": {
                    "text": dfDrug.iloc[i]["drug_frequency"],
                    "route": {
                      "coding": [
                        {
                          "system": "http://snomed.info/sct",
                          "code": "47625008",
                          "display": dfDrug.iloc[i]["drug_roa"]
                        }
                      ]
                    },
                    
                    
                  }
                                                           
                       
                
              }
        
        dict_json.update({str(i) : single_json}) 

    return(dict_json)
    
## Call the function to create the required json structure using
## dictionary.


dictJsonDrug = drug_dic_json(dfDrug)    


## Create the json file.

with open(pathofDrugJsonfile, 'w') as drugFjson:
    
    
    js.dump(dictJsonDrug,drugFjson)  
