#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 03:05:25 2020


This program reads the relevant csv files and then creates
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


pathOfDrugfile = '/data8/network_mount/S/CODA19_Anon_csv/drug_data.csv'
#pathofDrugJsonfile = '/data8/network_mount/S/FHIR_json/Final_Oct_21/drug_data.json'
pathofDrugJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/drug_data.json'



path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'

## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfDrug = pd.read_csv(pathOfDrugfile)



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





def drug_dic_json(dfDrug, dic_chum):
    
      
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    
    
    
    Arguments:
        
        Input: dfDrug type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    
    for i in range(len(dfDrug)):
        
        
        ## Fetch the array/list name.
        
        key_exist = dic_chum.get("drugRoute","None")
        
        if(key_exist == 'None'):
            
            
            system_input = 'http://snomed.info/sct'            
            code_input = ''                        
            display_complete_input = 'no code available'
            
            
            
        else:
                       
            
           for k in range(len(dic_chum["drugRoute"])):  
            
              if('snomed_code'in dic_chum["drugRoute"][k].keys()):  
                
                                        
                system_input = dic_chum["drugRoute"][k]['snomed_reference_url']            
                code_input = dic_chum["drugRoute"][k]['snomed_code']                       
                display_complete_input = dic_chum["drugRoute"][k]['raw_string_lower']
                
                break
            
              else:
              
                system_input = 'http://snomed.info/sct'            
                code_input = ''                        
                display_complete_input = 'no code available'
                
                #break
                  
                  
        
        key_exist_drug = dic_chum.get("drugCodes","None")
        
        
        if(key_exist_drug == 'None'):
            
            system_input_drug = "http://hl7.org/fhir/sid/ndc"           
            code_input_drug = ''                        
            display_complete_drug = ''
            
            
            
        else:
            
            
            
          for k in range(len(dic_chum["drugCodes"])):  
            
              
              if((dfDrug.at[i,"drug_code"])==(dic_chum["drugCodes"][k]['code'])):
            
                   system_input_drug = "http://hl7.org/fhir/sid/ndc"           
                   code_input_drug = dic_chum["drugCodes"][k]['code']                       
                   display_complete_drug = dic_chum["drugCodes"][k]['description']  
            
        
                   break
        
              else:
                  
                  system_input_drug = "http://hl7.org/fhir/sid/ndc"           
                  code_input_drug = ''                        
                  display_complete_drug = ''
        
        
        
        
        single_json = {
                  
                  

                  # The type of resource                    
                  
                  "resourceType": "MedicationAdministration",
                  
                  # Each resource entry needs a unique id for the ndjson bulk upload. 
                  
                  "id": dfDrug.iloc[i]["drug_uid"],
                  
                  "subject": {
                    
                          "reference": "Patient/pat1"
                    
                  },
                  

                  "contained": [
                    {
                      "resourceType": "Medication",
                      "id": dfDrug.iloc[i]["drug_name"],
                      "code": {
                        "coding": [
                          {
                            "system": system_input_drug,
                            "code": dfDrug.iloc[i]["drug_code"],
                            "display": display_complete_drug
                          }
                        ]
                      }
                    },
                    
                  ],
                  

                  
                  "effectivePeriod": {
                     # YYYY-MM-DDThh:mm:ss+zz:zz
                     "start": dfDrug.iloc[i]["drug_start_time"],
                     "end": dfDrug.iloc[i]["drug_end_time"]
                 },
                  
                  
                 "dosage": {
                    "text": dfDrug.iloc[i]["drug_frequency"],
                    "route": {
                      "coding": [
                        {
                          "system": system_input,
                          "code": code_input,
                          "display": dfDrug.iloc[i]["drug_roa"]
                        }
                      ]
                    },
                    
                    
                  }
                                                           
                       
                
              }
        
        dict_json.update({str(i) : single_json}) 

    return(dict_json)
    



## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary)
           

#for i in dict_data["drugRoute"]: 
    
        
    #print(i)
 

## Replace drug_frequency that are empty with '' to avoid issues later.

dfDrug['drug_frequency'].fillna('None', inplace = True)

## Call the function to create the required json structure using
## dictionary.


dictJsonDrug = drug_dic_json(dfDrug, dict_data)    


## Create the json file.

with open(pathofDrugJsonfile, 'w') as drugFjson:
    
    
    js.dump(dictJsonDrug,drugFjson)  
