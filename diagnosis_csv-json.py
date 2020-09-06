#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:25:42 2020


This program reads  the relevant csv files and then creates
a json file using the data retrieved based on the FHIR
structure.




@author: rdas
"""





import numpy as np
import pandas as pd
import json as js
import csv as cv


## Define the paths (The paths here are those that considered the CITADEL infrastructure)

pathOfDiagnosisfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/diagnosis_data.csv'
pathofDiagnosisJsonfile = '/data8/network_mount/S/FHIR_json/diagnosis_data.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfDiagnosis = pd.read_csv(pathOfDiagnosisfile)



def diagnosis_dic_json(dfDiagnosis):
    
    
        
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfDiagnosis type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
   
    
    for i in range(len(dfDiagnosis)):
    
    

        single_json = { 
                             
                            # The type of resource
                
                            "resourceType": "Condition",
                            
                            # Each resource entry needs a unique id for the ndjson bulk upload
                            
                            "id": "Provide id here",
                            
                                             
                           
                            "subject": {
                                 
                               "reference": "Patient/example"
                            },
                          

                            # Clinical episode associated with the observation (if possible)
                            
                            "encounter": {"reference": "Encounter/2314234"},

                      
                            "onsetString": dfDiagnosis.iloc[i]["diagnosis_time"],
                          
                          
                            "code": {
                              
                              "coding": [
                                  {
                                        # SNOMED code for the diagnosis (SNOMED field to be omitted until coding/categorization completed) 
                            	
                            				"system": "http://snomed.info/sct",
                            				"code": "422504002",
                            				"display": "Ischemic stroke (disorder)"
                                        # Sites may have ICD-10 codes for diagnoses, please include here if so.  
                                  }, 
                                          
                                  {
                            				"system": "http://hl7.org/fhir/ValueSet/icd-10",
                            				"code": "I63.9",
                            				"display": "Cerebral infarction, unspecified"
                            		 }
                               
                                ],
                               
                                "text": "Stroke"
                                                      
                                  
                            }                
                                                               
                                          
                          
                      }
                       
        dict_json.update({str(i) : single_json}) 

    return(dict_json)   



## Call the function to create the required json structure using
## dictionary.


dictJsonDiagnosis = diagnosis_dic_json(dfDiagnosis)    


## Create the json file.

with open(pathofDiagnosisJsonfile, 'w') as diagnosisFjson:
    
    
    js.dump(dictJsonDiagnosis,diagnosisFjson)           
