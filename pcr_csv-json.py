#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 21:57:50 2020

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


pathOfPcrfile = '/data8/network_mount/S/CODA19_Anon_csv/pcr_data.csv'
#pathofPcrJsonfile = '/data8/network_mount/S/FHIR_json/Final_Oct_21/pcr_data.json'
pathofPcrJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/pcr_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfPcr = pd.read_csv(pathOfPcrfile)



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



def pcr_dic_json(dfPcrData, dic_chum):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    Arguments:
        
        Input: dfPcrData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfPcrData)):
        
        
        ## Fetch the array/list name.
        
        key_exist = dic_chum.get("pcrResultStatus","None")
        
        
        if(key_exist == 'None'):
            
            
            system_input = 'http://snomed.info/sct'            
            code_input = ''                        
            display_complete_input = 'no code available'
            
            
            
        else:
            
            
            ## consider the dictionary/object in the json dictionary using the key and fetch
            ## the values. Here the first three characters are considered to perform a match
            ## check. In the present scenario this was a simpler approach.   
            
            
          for k in range(len(dic_chum["pcrResultStatus"])):   
            
                     
            string_check = dic_chum["pcrResultStatus"][k]['raw_string_lower']  
            
            if(string_check == 'négatif'):
                
             
               string_check = string_check[:3].replace('é','e')
               
                              
            elif(string_check == 'non détecté'): 
                
                string_check = 'negative'
                
            elif(string_check == 'test annulé' or string_check == 'annulé' or string_check == 'non valide'):    # one may have to change this
                
                string_check = 'can'
                
            else:    
            
                
               string_check = string_check[:3] 
               
               
              
            if((string_check)==(dfPcr.at[i,'pcr_result_value'][:3])):   #raw_string_lower  
              
              if('result_snomed_code'in dic_chum["pcrResultStatus"][k].keys()):
             
                system_input = dic_chum["pcrResultStatus"][k]['snomed_reference_url']            
                code_input = dic_chum["pcrResultStatus"][k]['result_snomed_code']                       
                display_complete_input = dic_chum["pcrResultStatus"][k]['raw_string_lower']
        
                break
        
                
        ## Fetch the array/list name.
        
        key_exist_loinc = dic_chum.get("pcrName","None")

 
        if(key_exist_loinc == 'None'):
            
            
            system_input_loinc = 'http://loinc.org'            
            code_input_loinc = ''                        
            display_complete_input_loinc = 'no code available'
            
          
        else:   
                
          
          for k in range(len(dic_chum["pcrName"])):  
            
              
             airtable_entries_present = True 
              
             if((dic_chum["pcrName"][k]['display_string'])==(dfPcr.at[i,'pcr_name'])):   #raw_string_lower
              
                if('loinc_code'in dic_chum["pcrName"][k].keys()):
              
                  system_input_loinc = dic_chum["pcrName"][k]['loinc_reference_url']       # dic_chum["pcrName"][k]['loinc_reference_url']            
                  code_input_loinc = dic_chum["pcrName"][k]['loinc_code']                       
                  display_complete_input_loinc = dic_chum["pcrName"][k]['display_string']
                  
                  airtable_entries_present = False                         
                  
                  break
                  
                else:
                    
                                   
                  system_input_loinc = 'http://loinc.org'            
                  code_input_loinc = ''                       
                  display_complete_input_loinc = 'no code available may require entry in the Airtable.'  
             
                  airtable_entries_present = True
                  
                 
                
             if(airtable_entries_present):
                
                 system_input_loinc = 'http://loinc.org'            
                 code_input_loinc = ''                       
                 display_complete_input_loinc = 'no code available may require entry in the Airtable.' 
                 
       
       
        
        
        single_json = { 
                
                            # The type of resource
                            
                            "resourceType" : "Observation",
                           
                             # Each resource entry needs a unique id for the ndjson bulk upload.
                            
                            "id": dfPcrData.iloc[i]["pcr_uid"],

                             
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
                                    
                                   { "system" : system_input_loinc,
                                     "code": code_input_loinc,
                                     "display": ""
                                     }
                            
                            ],
                            
                            "text": dfPcrData.iloc[i]["pcr_name"]
                            
                            },
                            
                            # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)
                            
                            "bodySite": {
                               
                               "coding": [ 
                                
                                {"system": system_input ,
                                           "code" : code_input,
                                           "display": dfPcrData.iloc[i]["pcr_sample_type"]}
                                ]
                               
                               },
                            
                            "valueQuantity": {"value": dfPcrData.iloc[i]["pcr_result_value"],
                                              "unit": "",
                                              "system": "",
                                              "code": ""}
                                    
                                     
                                     
                       }
                        
        dict_json.update({str(i) : single_json})

    return(dict_json)
    




## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 


## debug

#for i in dict_data["pcrResultStatus"]: 
    
    #print(i)
   

## Replace pcr_result_value that are empty with none to avoid issues later.

dfPcr['pcr_result_value'].fillna('None', inplace = True)

## Call the function to create the required json structure using
## dictionary.

dictJsonPcr = pcr_dic_json(dfPcr, dict_data)    


## Create the json file.

with open(pathofPcrJsonfile, 'w') as pcrFjson:
    
    
    js.dump(dictJsonPcr,pcrFjson)
