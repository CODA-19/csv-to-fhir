#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 11:45:24 2020

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



#pathOfEpifile = '/data8/projets/Mila_covid19/output/covidb_anon/csv/episode_data.csv'



pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/episode_data.csv'
pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Feb_10/episode_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfEpi = pd.read_csv(pathOfEpifile)



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



    
    
def epi_dic_json(dfepisode,dic_chum):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfepisode type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    dict_json = {}
    
    for i in range(len(dfepisode)):
        
        
        
        
        ## Fetch the array/list name.
        
        key_exist = dic_chum.get("unitType","None")
        
        
        if(key_exist == 'None'):
            
            
            system_input = 'http://terminology.hl7.org/ValueSet/v3-ServiceDeliveryLocationRoleType'            
            code_input = ''                        
            display_complete_input = 'no code available'
            
            
            
        else:
        
          
          ## consider the dictionary/object in the json dictionary using the key and fetch
          ## the values. Here the first three characters are considered to perform a match
          ## check. In the present scenario this was a simpler approach.   
            
            
          for k in range(len(dic_chum["unitType"])):   
           
              
             
               string_check = dic_chum["unitType"][k]['display_string'][:5]
               
               
              
               if(string_check == dfepisode.iloc[i]["episode_unit_type"][:5]):   
                              
                   system_input = dic_chum["unitType"][k]['fhir_reference_url']          
                   code_input = dic_chum["unitType"][k]['fhir_code']                        
                   display_complete_input = dic_chum["unitType"][k]['display_string']
                   
                   
                   
                   break
                   
               else:
                   
                   system_input = 'http://terminology.hl7.org/ValueSet/v3-ServiceDeliveryLocationRoleType'            
                   code_input = ''                        
                   display_complete_input = 'no code available'                
                   
        
         
        
        
        
        
        single_json = { 
                
                
                           "resourceType" : "Encounter",
                           
                           "id": dfepisode.iloc[i]["episode_admission_uid"],    ## dfepisode.iloc[i]["patient_site_uid"]                                   
                                                              
                                                                                  
                           "class": {"system": "http://terminology.hi17.org/CodeSystem/v3-ActCode",                     
                                                                            
                                      "code": 'IMP',                         
                                      "display": dfepisode.iloc[i]["episode_description"]},        
                                      
                           
                           "subject":{"reference": str(dfepisode.iloc[i]["patient_site_uid"])},
                           
                           "location": [ {                                    
                                         "location":{ "reference": code_input,
                                         "display":  display_complete_input
                                       },
                                   
                                       "status": "completed",
                                       
                                       "period": {
                                                  "start": dfepisode.iloc[i]["episode_start_time"],
                                                  "end": dfepisode.iloc[i]["episode_end_time"]
                                                  }
                                       
                                       }
                                   
                                   ],
                           
                           
                           
                           "reasonCode": [
                                	{
                                	  "text": "This patient was hospitalized for Condition X"
                                	}
                           ],
                             
                                                     
                           "period": {"start":  dfepisode.iloc[i]["episode_start_time"] ,
                                        "end": dfepisode.iloc[i]["episode_end_time"] }
                                                
                       }
    
        dict_json.update({str(i) : single_json})
    
        
    
    return(dict_json)
 




## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 





## Call the function to create the required json structure using
## dictionary.


dictJsonEpi = epi_dic_json(dfEpi,dict_data)

## dictJsonEpi["17808"] #check
       


## Create the json file.

with open(pathofEpiJsonfile, 'w') as epiFjson:
    

    
    js.dump(dictJsonEpi,epiFjson)
    
    
