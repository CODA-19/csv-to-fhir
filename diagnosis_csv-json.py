#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:25:42 2020


This program reads  the relevant csv files and then creates
a json file using the data retrieved based on the FHIR
structure.



The column ending with '_uid' other than patient_site_uid
was added to allow the generated files to work in the Aidbox
environment. The values in this column do not exist in the
source csv file. They are generated using random-hex number
generator, and this may change later.




@author: rdas
"""





import numpy as np
import pandas as pd
import json as js
import csv as cv


## Define the paths (The paths here are those that considered the CITADEL infrastructure)


pathOfDiagnosisfile = '/data8/network_mount/S/CODA19_Anon_csv/diagnosis_data.csv'
#pathofDiagnosisJsonfile = '/data8/network_mount/S/FHIR_json/Final_Oct_21/diagnosis_data.json'
pathofDiagnosisJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/diagnosis_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'




## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfDiagnosis = pd.read_csv(pathOfDiagnosisfile)



def read_dictionary(path_to_dictionary_file):
    
    
    """
    
    Considers path of the json file. 
    
    
    Arguments:
        
        path_to_setting_file: A string
        
    Returns: 
        
        data: Object 
    
    
    """
    
   
    try:
        with open(path_to_dictionary_file) as data_file:
            data = js.load(data_file)
            data_file.close()
            return data
    
    except IOError as e:
        
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        return -1






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
                            
                            "id": dfDiagnosis.iloc[i]["diagnosis_uid"],
                            
                                             
                           
                            "subject": {
                                 
                               "reference": "Patient/example"
                            },
                          

                            # Clinical episode associated with the observation (if possible)
                            
                            "encounter": {"reference": "Encounter/2314234"},

                      
                            "onsetString": dfDiagnosis.iloc[i]["diagnosis_time"],
                          
                          
                            "code": {
                              
                              "coding": [
                                                                           
                                  {
                            				"system": "http://hl7.org/fhir/ValueSet/icd-10",
                            				"code": dfDiagnosis.iloc[i]["diagnosis_icd_code"],
                            				"display": dfDiagnosis.iloc[i]["diagnosis_name"]
                            		 }
                               
                                ],
                               
                                "text": dfDiagnosis.iloc[i]["diagnosis_name"]
                                                      
                                  
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
