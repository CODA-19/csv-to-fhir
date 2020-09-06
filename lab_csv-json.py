#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 13:34:09 2020


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

pathOfLabfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/lab_data.csv'
pathofLabJsonfile = '/data8/network_mount/S/FHIR_json/lab_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfLab = pd.read_csv(pathOfLabfile)






def lab_dic_json(dfLabData):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfLabData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfLabData)):
        
        single_json = { 
                                
                            # The type of resource            
                
                            "resourceType" : "Observation",
                                                     
                            # Each resource entry needs a unique id for the ndjson bulk upload. 
                            
                            "id": "Provide id here",
                                                                        
                             
                            # The status of the observation: registered | preliminary | final | amended 
                            
                            "status": dfLabData.iloc[i]["lab_result_status"],
                            
                            
                            # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "effectiveDateTime" : dfLabData.iloc[i]["lab_sample_time"],
                            
                            
                            # Time result issued (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "issued": dfLabData.iloc[i]["lab_result_time"],
                            
                            # Patient associated with the observation
                            
                            "subject" : {"reference" : str(dfLabData.iloc[i]["patient_site_uid"])},
                            
                           
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
                            
                            "text": dfLabData.iloc[i]["lab_name"]
                            
                            },
                              
                            # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)  
                                                    
                            "bodySite": {
                               
                               "coding": [ 
                                
                                {"system": "http://snomed.info/sct",
                                           "code" : "122555007",
                                           "display": dfLabData.iloc[i]["lab_sample_type"]
                                          }
                                ]
                               
                               },
                            
                            # Value and units of measure
                            
                            "valueQuantity": {"value": dfLabData.iloc[i]["lab_result_value_string"],
                                              "unit":  dfLabData.iloc[i]["lab_result_units"],
                                              "system": "http://unitsofmeasure.org",
                                              "code": "m-3.g"}
                                                                      
                                     
                       }
                        
        dict_json.update({str(i) : single_json})

    return(dict_json)
            
    
## Call the function to create the required json structure using
## dictionary.


dictJsonLab = lab_dic_json(dfLab)    


## Create the json file.

with open(pathofLabJsonfile, 'w') as labFjson:
    
    
    js.dump(dictJsonLab,labFjson)
