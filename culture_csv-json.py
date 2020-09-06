#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 19:02:17 2020

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

pathOfCulturefile = '/data8/projets/Mila_covid19/output/covidb_full/csv/culture_data.csv'
pathofCultureJsonfile = '/data8/network_mount/S/FHIR_json/culture_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfCulture = pd.read_csv(pathOfCulturefile)






def culture_dic_json(dfCulture):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfCulture type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfCulture)):
        
        if (pd.isna(dfCulture.iloc[i]["culture_growth_positive"])):
            
           
            dfCulture.at[i,"culture_growth_positive"] = "pending"
        
        single_json = { 
                            # The type of resource               
                
                            "resourceType" : "Observation",
                                           
                            # Each resource entry needs a unique id for the ndjson bulk upload. 
                            
                            "id": "Provide id here",
                                
                            
                            # The status of the observation: registered | preliminary | final | amended
                                              
                            "status": dfCulture.iloc[i]["culture_result_status"],
                            
                            # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "effectiveDateTime" : dfCulture.iloc[i]["culture_sample_time"],
                            
                            #  Time result issued (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "issued": dfCulture.iloc[i]["culture_result_time"], 
                            
                            # Patient associated with the observation
                            
                            "subject" : {"reference" : "Patient/3294843"},
                            
                            # Clinical episode associated with the observation (if possible)
                            
                            "encounter": {"reference": "Encounter/2314234"},
                            
                            # LOINC code for the observation that was made (LOINC "code" field to be omitted until coding/categorization completed)
                            
                            "code": {
                                    
                              "coding": [     
                                    
                                   {"system" : "http://loinc.org",
                                     "code": "718-7",
                                     "display": "Hemoglobin [Mass/volum] in Blood"
                                     }
                            
                            ],
                            
                            "text": dfCulture.iloc[i]["culture_type"]
                            
                            },
                              
                            # SNOMED code for the method used (SNOMED "code" field to be omitted until coding/categorization completed)   
                              
                            "method": {
                               
                               "coding": [ 
                                
                                {"system": "http://snomed.info/sct" ,
                                           "code" : "122555007",
                                           "display": dfCulture.iloc[i]["culture_sample_type"]}
                                ]
                               
                               },
                            
                            "interpretation": [{
                               
                               "coding": [{
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                            "code": "POS"
                                         }]
                             }]
                                    
                                     
                                     
                       }
                        
        dict_json.update({str(i) : single_json})
       

    
    return(dict_json)
            
    
## Call the function to create the required json structure using
## dictionary.


dictJsonCulture = culture_dic_json(dfCulture)    


## Create the json file.

with open(pathofCultureJsonfile, 'w') as cultureFjson:
    
    
    js.dump(dictJsonCulture,cultureFjson)