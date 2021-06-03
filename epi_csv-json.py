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
import enum


## Define the paths (The paths here are those that considered the CITADEL infrastructure)



#pathOfEpifile = '/data8/projets/Mila_covid19/output/covidb_anon/csv/episode_data.csv'



#pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/april_16_data/episode_data.csv'
#pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Apr_16/episode_data.json'


pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/episode_data.csv'
pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/episode_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'



location_dict = {'HU' : '016873897351baee68fe5e9fa80ec993c64d4d1b', 'CHR':'cd411fa348c52293e1d0c96328c3069234e91037', \
                 'ICU': 'e70a812f1f88c5dedeb74a666923b6ae3d0b66da' , 'CCU' : '24342cdc69f186636c4fe5c694bc5314ece67a83' , \
                 'CATH': '3e5d20d40084825438cf4fd23ff7008ddd67c835' , 'ER' : '284d5c512615ea2ebc89111076c0e99403f6fd66' , \
                 'UNK': '0000000000000000000000000000000000000000'}


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
                   code_input = 'UNK'                        
                   display_complete_input = 'no code available'                
          
                 
        
        single_json = { 
                
                
                           "resourceType" : "Encounter",
                           
                           "id": dfepisode.iloc[i]["episode_admission_uid"],    ## dfepisode.iloc[i]["patient_site_uid"]                                   
                                                              
                                                                                  
                           "class": {"system": "http://terminology.hi17.org/CodeSystem/v3-ActCode",                     
                                                                            
                                      "code": 'IMP',                         
                                      "display": dfepisode.iloc[i]["episode_description"]},        
                                      
                           
                           "subject":{"reference": 'Patient' + '/' + str(dfepisode.iloc[i]["patient_site_uid"])},
                           
                           "location": [ { 
                                                                            
                                         "location":{ 
                                         
                                         "system": 'https://www.hl7.org/fhir/v3/ServiceDeliveryLocationRoleType/vs.html',        
                                         "reference": 'Location' + '/' + str(location_dict[code_input]),
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
 




## load the dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 


## Fill the missing episode_unit_type with unknown.

dfEpi['episode_unit_type'].fillna('unknown', inplace = True)


## Replace episode_description that are na  with "" to avoid issues later.

dfEpi['episode_description'].fillna('', inplace = True)



## Call the function to create the required json structure using
## dictionary.


dictJsonEpi = epi_dic_json(dfEpi,dict_data)

## dictJsonEpi["17808"] #check
       


## Create the json file.

with open(pathofEpiJsonfile, 'w') as epiFjson:
    

    
    js.dump(dictJsonEpi,epiFjson)
    
    
