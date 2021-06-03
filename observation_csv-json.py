#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 02:10:26 2020


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


#pathOfObservationfile = '/data8/network_mount/S/CODA19_Anon_csv/april_data/observation_data.csv'
#pathofObservationJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Apr_8/observation_data.json'
#pathofEpifile = '/data8/network_mount/S/CODA19_Anon_csv/april_data/episode_data.csv'



pathOfObservationfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/observation_data.csv'
pathofEpifile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/episode_data.csv'
pathofObservationJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/observation_data.json'




path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'






## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfObservation = pd.read_csv(pathOfObservationfile)


dfEpi = pd.read_csv(pathofEpifile)



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



def observation_dic_json(dfObservation, dic_chum):
    
      
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    
    Arguments:
        
        Input: dfObservation type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    
    for i in range(len(dfObservation)):
    
         
        ## Fetch the array/list name.
        
        key_exist = dic_chum.get("observationNameUnit","None")
        
        
        if(key_exist == 'None'):
            
            
            system_input_loinc = 'http://loinc.org'            
            code_input = ''                        
            display_complete_input = 'no code available'
            
            
            
        else:
            
            ## consider the dictionary/object in the json dictionary using the key and fetch
            ## the values. Here the first three characters are considered to perform a match
            ## check. In the present scenario this was a simpler approach.
            
            for k in range(len(dic_chum["observationNameUnit"])):  
                
                
                            
              sub_string_to_check = dic_chum["observationNameUnit"][k]['raw_string_lower'][:3] 
              
              if(sub_string_to_check == 'pou'):
                  
                  sub_string_to_check = 'pul'
                  
              elif(sub_string_to_check == 'sao'or sub_string_to_check == 'sat'):
                   
                  sub_string_to_check = 'oxy' 
                
              elif(sub_string_to_check == 'ryt'):
                  
                  sub_string_to_check = 'res'
                  
                  
                
              
              if((dfObservation.at[i,"observation_name"][:3])==(sub_string_to_check)):  
                
              
                   ## Debug
                  
                   #print(sub_string_to_check[:3])
                   
                   
                
                   system_input_loinc = dic_chum["observationNameUnit"][k]['loinc_reference_url']             
                   code_input =  dic_chum["observationNameUnit"][k]['name_loinc_code']                  
                   display_complete_input = dic_chum["observationNameUnit"][k]['raw_string_lower']
                   ucum_code =  dic_chum["observationNameUnit"][k]['unit_ucum_code']  
                   ucum_reference = dic_chum["observationNameUnit"][k]['ucum_reference_url'] 
                   
                  
                   
                   break
        
        
        
        
        
        indexfor_episode = dfEpi[dfEpi['patient_site_uid']== dfObservation.iloc[i]["patient_site_uid"]].index
        
        #episode_uid = dfEpi.iloc[indexfor_episode[0]]['episode_admission_uid']
        
        
    
        single_json = {
                  
                          # The type of resource            
                          
                          "resourceType": "Observation",
                          
                          # Each resource entry needs a unique id for the ndjson bulk upload. 
                          
                          "id": dfObservation.iloc[i]["observation_uid"],                                    
                           
                          # The status of the observation                                                                   
                              
                          "status": "final",
                         
                          # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                          
                          "effectiveDateTime" : dfObservation.iloc[i]["observation_time"],
                         
                                                  
                          # Patient associated with the observation
                            
                          "subject" : {"reference" : "Patient" + '/' + str(dfObservation.iloc[i]["patient_site_uid"])},
                         
                       
                          # Clinical episode associated with the observation (if possible) 
                         
                          "encounter": {"reference": "Encounter/2314234"},
                         
                         
                          # LOINC code for the observation that was made (LOINC "code" field to be omitted until coding/categorization completed)
                         
                          "code": {
                                    
                              "coding": [     
                                    
                                   {"system" : system_input_loinc,
                                    "code": code_input,
                                    "display": ""
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
                                              "unit": ucum_code,
                                              "system": ucum_reference,
                                              "code": ""}     
                              
                       
                
              }
        
        dict_json.update({str(i) : single_json}) 

    return(dict_json)
    
 

## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary)    
    



## Debug
     
#for i in dict_data["observationNameUnit"]: 
    
    #print(i)





## Call the function to create the required json structure using
## dictionary.


dictJsonObservation = observation_dic_json(dfObservation, dict_data)    


## Create the json file.

with open(pathofObservationJsonfile, 'w') as observationFjson:
    
    
    js.dump(dictJsonObservation,observationFjson)    
