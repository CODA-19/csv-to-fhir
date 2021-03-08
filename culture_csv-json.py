#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 19:02:17 2020

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


pathOfCulturefile = '/data8/network_mount/S/CODA19_Anon_csv/culture_data.csv'
#pathofCultureJsonfile = '/data8/network_mount/S/FHIR_json/Final_Oct_21/culture_data.json'
pathofCultureJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/culture_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfCulture = pd.read_csv(pathOfCulturefile)



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


def culture_dic_json(dfCulture, dic_chum):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    
    Arguments:
        
        Input: dfCulture type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfCulture)):
        
        
        
        
        if (pd.isna(dfCulture.iloc[i]["culture_growth_positive"])):
            
           
            dfCulture.at[i,"culture_growth_positive"] = "pending"
            
           
        ## Fetch the array/list name.    
            
        key_exist = dic_chum.get("cultureResultStatus","None")
        
        
        if(key_exist == 'None'):
            
            
            system_input = 'http://snomed.info/sct'            
            code_input = ''                        
            display_input = 'no code available'
            
            
            
        else:
                      
         
                   
            
           for k in range(len(dic_chum.get("cultureResultStatus"))):
               
               if((dic_chum["cultureResultStatus"][k]['raw_string_lower'])==(dfCulture.at[i,"culture_growth_positive"][:3])):

                    
                   system_input = dic_chum["cultureResultStatus"][k]['snomed_reference_url']             
                   code_input =  dic_chum["cultureResultStatus"][k]['result_snomed_code']            
                   display_complete_input =  dic_chum["cultureResultStatus"][k]['result_display_string']            
                   display_input = dic_chum["cultureResultStatus"][k]['result_display_string']
                   
                   break
        
        
        
         ## Fetch the array/list name.
        
        key_exist_loinc = dic_chum.get("cultureName","None")
        
        
        if(key_exist_loinc == 'None'):
            
            
            system_input_loinc = 'http://loinc.org'            
            code_input = ''                        
            display_complete_input_loinc = 'no code available'
            
            
            
        else:
            
          
          for k in range(len(dic_chum["cultureName"])): 
        

              if((dic_chum["cultureName"][k]['display_string'])==(dfCulture.at[i,"culture_type"])):
                  
                 
                    system_input_loinc = dic_chum["cultureName"][k]['loinc_url_computed']           
                    code_input_loinc = dic_chum["cultureName"][k]['loinc_code']                      
                    display_complete_input_loinc = dic_chum["cultureName"][k]['display_string']
                 
                    
                    break 
                
        
        single_json = { 
                            # The type of resource               
                
                            "resourceType" : "Observation",
                                           
                            # Each resource entry needs a unique id for the ndjson bulk upload. 
                            
                            "id": dfCulture.iloc[i]["culture_uid"], ## This will be changed.
                                
                            
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
                                    
                                   {"system" : system_input_loinc,
                                     "code": code_input_loinc,
                                     "display": display_complete_input_loinc
                                     }
                            
                            ],
                            
                            "text": dfCulture.iloc[i]["culture_type"]
                            
                            },
                              
                            # SNOMED code for the method used (SNOMED "code" field to be omitted until coding/categorization completed)   
                              
                            "method": {
                               
                               "coding": [ 
                                
                                {"system": system_input,
                                           "code" : code_input,
                                           "display": dfCulture.iloc[i]["culture_sample_type"]}
                                                                                                                                
                                ]                             
                          
                               
                               
                               },
                            
                            "interpretation": [{
                               
                               "coding": [{
                                            "system": system_input,
                                            "code": display_input
                                         }]
                             }],
                                                                    
                               
                              
                               
                               
                               
                                     
                       }
                        
        dict_json.update({str(i) : single_json})
       

    
    return(dict_json)
 



## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary)
           

## Debug

#for i in dict_data["cultureResultStatus"]: 
    
    #print(i)



# Call the function to create the required json structure using
## dictionary.


dictJsonCulture = culture_dic_json(dfCulture, dict_data)    


## Create the json file.

with open(pathofCultureJsonfile, 'w') as cultureFjson:
    
    
    js.dump(dictJsonCulture,cultureFjson)