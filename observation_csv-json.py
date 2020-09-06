#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 02:10:26 2020


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

pathOfObservationfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/observation_data.csv'
pathofObservationJsonfile = '/data8/network_mount/S/FHIR_json/observation_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfObservation = pd.read_csv(pathOfObservationfile)



def observation_dic_json(dfObservation):
    
      
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfObservation type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    
    for i in range(len(dfObservation)):
    
    
    
        single_json = {
                  
                          # The type of resource            
                          
                          "resourceType": "Observation",
                          
                          # Each resource entry needs a unique id for the ndjson bulk upload. 
                          
                          "id": "Provide id here",                                    
                           
                          # The status of the observation                                                                   
                              
                          "status": "final",
                         
                          # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                          
                          "effectiveDateTime" : dfObservation.iloc[i]["observation_time"],
                         
                                                  
                          # Patient associated with the observation
                            
                          "subject" : {"reference" : str(dfObservation.iloc[i]["patient_site_uid"])},
                         
                       
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
                            
                          "text": dfObservation.iloc[i]["observation_name"]
                            
                          },
                              
                          
                          # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)  
                                                    
                          "bodySite": {
                               
                             "coding": [ 
                                
                               {"system": "http://snomed.info/sct" ,
                                          "code" : "368209003",
                                          "display": "Right arm"}
                               ]
                               
                          },
                            
                          # Value and units of measure 
                           
                          "valueQuantity": {"value": dfObservation.iloc[i]["observation_value"],
                                              "unit": "mmHg",
                                              "system": "http://unitsofmeasure.org",
                                              "code": "m-3.g"}     
                              
                       
                
              }
        
        dict_json.update({str(i) : single_json}) 

    return(dict_json)
    
    
    
    
## Call the function to create the required json structure using
## dictionary.


dictJsonObservation = observation_dic_json(dfObservation)    


## Create the json file.

with open(pathofObservationJsonfile, 'w') as observationFjson:
    
    
    js.dump(dictJsonObservation,observationFjson)    
