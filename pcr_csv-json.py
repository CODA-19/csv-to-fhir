#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 21:57:50 2020

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

pathOfPcrfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/pcr_data.csv'
pathofPcrJsonfile = '/data8/network_mount/S/FHIR_json/pcr_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfPcr = pd.read_csv(pathOfPcrfile)





def pcr_dic_json(dfPcrData):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfPcrData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfPcrData)):
        
        single_json = { 
                
                            # The type of resource
                            
                            "resourceType" : "Observation",
                           
                             # Each resource entry needs a unique id for the ndjson bulk upload.
                            
                            "id": "Provide id here",

                             
                            # The status of the observation: registered | preliminary | final | amended 
                                                                         
                            "status": dfPcrData.iloc[i]["pcr_result_status"],
                            
                            # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "effectiveDateTime" : dfPcrData.iloc[i]["pcr_sample_time"],
                            
                            # Patient associated with the observation
                            
                            "issued": dfPcrData.iloc[i]["pcr_result_time"],
                            
                            # This needs to be associated with patient_site_id (how we can join labs to the patient table)
                            
                            "subject" : {"reference" : str(dfPcrData.iloc[i]["patient_site_uid"])},
                            
                            # Clinical episode associated with the observation (if possible)
                            
                            "encounter": {"reference": "Encounter/2314234"},
                            
                            # LOINC code for the observation that was made (LOINC "code" field to be omitted until coding/categorization completed)
                            
                            "code": {
                                    
                              "coding": [     
                                    
                                   { "system" : "http://loinc.org",
                                     "code": "718-7",
                                     "display": "Hemoglobin [Mass/volum] in Blood"
                                     }
                            
                            ],
                            
                            "text": dfPcrData.iloc[i]["pcr_name"]
                            
                            },
                            
                            # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)
                            
                            "bodySite": {
                               
                               "coding": [ 
                                
                                {"system": "http://snomed.info/sct" ,
                                           "code" : "122555007",
                                           "display": dfPcrData.iloc[i]["pcr_sample_type"]}
                                ]
                               
                               },
                            
                            "valueQuantity": {"value": dfPcrData.iloc[i]["pcr_result_value"],
                                              "unit": "g/L",
                                              "system": "http://unitsofmeasure.org",
                                              "code": "m-3.g"}
                                    
                                     
                                     
                       }
                        
        dict_json.update({str(i) : single_json})

    return(dict_json)
    
    

## Call the function to create the required json structure using
## dictionary.


dictJsonPcr = pcr_dic_json(dfPcr)    


## Create the json file.

with open(pathofPcrJsonfile, 'w') as pcrFjson:
    
    
    js.dump(dictJsonPcr,pcrFjson)
