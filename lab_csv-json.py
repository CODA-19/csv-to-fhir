#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 13:34:09 2020


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


pathOfLabfile = '/data8/network_mount/S/CODA19_Anon_csv/lab_data.csv'
pathofLabJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/lab_data.json'



path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfLab = pd.read_csv(pathOfLabfile)





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







def lab_dic_json(dfLabData,dic_chum):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    
    Arguments:
        
        Input: dfLabData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfLabData)):
        
        
        ## Fetch the array/list name.
        
        key_exist_loinc = dic_chum.get("labName","None")
        
        
        if(key_exist_loinc == 'None'):
            
            
            system_input_loinc = 'http://loinc.org'            
            code_input = ''                        
            display_complete_input = 'no code available'
            
            
            
        else:
            
          
          for k in range(len(dic_chum["labName"])):  
            
            
            if((dic_chum["labName"][k]['display_string'])==(dfLabData.at[i,'lab_name'])):  
              
                if('loinc_code'in dic_chum["labName"][k].keys()):    # this could be removed later.
                  
                    system_input_loinc = dic_chum["labName"][k]['loinc_url_computed']            
                    code_input =  dic_chum["labName"][k]['loinc_code']                  
                    display_complete_input = dic_chum["labName"][k]['display_string']  #raw_string_lower
                    
                    break
        
        ## Fetch the array/list name.
        
        key_exist_snomed = dic_chum.get("labSite","None")    

        
        if(key_exist_snomed == 'None'):
            
            
            system_input_snomed = 'http://snomed.info/sct'            
            code_input = ''                        
            display_complete_input_snomed = 'no code available'
                     
            
        else:
            
            
           for k in range(len(dic_chum["labSite"])):  
            
            
              if((dic_chum["labSite"][k]['display_string'])==(dfLabData.at[i,'lab_sample_type'])): 
            
            
                 if('snomed_url_computed'in dic_chum["labSite"][k].keys()): 
                  
                      system_input_snomed = dic_chum["labSite"][k]['snomed_url_computed']            
                      code_input_snomed =  dic_chum["labSite"][k]['snomed_code']                  
                      display_complete_input_snomed = dic_chum["labSite"][k]['display_string']  #raw_string_lower
                        
                      break
        
             
              else:  
        
        
                  system_input_snomed = 'http://snomed.info/sct'            
                  code_input_snomed =  ''                 
                  display_complete_input_snomed = 'no code available' 
        
        
        single_json = { 
                                
                            # The type of resource            
                
                            "resourceType" : "Observation",
                                                     
                            # Each resource entry needs a unique id for the ndjson bulk upload. 
                            
                            "id": dfLabData.iloc[i]["lab_uid"],
                                                                        
                             
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
                                    
                                   { "system" : system_input_loinc,                                      
                                     "code": code_input,
                                     "display": display_complete_input
                                     }
                            
                            ],
                            
                            "text": dfLabData.iloc[i]["lab_name"]
                            
                            },
                              
                            # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)  
                                                    
                            "bodySite": {
                               
                               "coding": [ 
                                
                                {"system": system_input_snomed,
                                           "code" : code_input_snomed,
                                           "display": dfLabData.iloc[i]["lab_sample_type"]
                                          }
                                ]
                               
                               },
                            
                            # Value and units of measure
                            
                            "valueQuantity": {"value": dfLabData.iloc[i]["lab_result_value_string"],
                                              "unit":  dfLabData.iloc[i]["lab_result_units"],
                                              "system": "",
                                              "code": ""}
                                                                      
                                     
                       }
                        
        dict_json.update({str(i) : single_json})

    return(dict_json)
            



## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 


## Debug

#for i in dict_data["labName"]: 
    
#    print(i)




    
## Call the function to create the required json structure using
## dictionary.


dictJsonLab = lab_dic_json(dfLab, dict_data)    


## Create the json file.

with open(pathofLabJsonfile, 'w') as labFjson:
    
    
    js.dump(dictJsonLab,labFjson)
