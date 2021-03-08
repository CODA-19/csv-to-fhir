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


#pathOfEpifile = '/data8/projets/Mila_covid19/output/covidb_full/csv/episode_data.csv'
#pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/episode_data.json'



#pathOfEpifile = '/data8/projets/Mila_covid19/output/covidb_anon/csv/episode_data.csv'
#pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Final_Sep_21/episode_data.json'


pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/episode_data.csv'
pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/episode_data.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfEpi = pd.read_csv(pathOfEpifile)




    
    
def epi_dic_json(dfepisode):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfepisode type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    dict_json = {}
    
    for i in range(len(dfepisode)):
        
        single_json = { 
                
                
                           "resourceType" : "Encounter",
                           
                           "id": dfepisode.iloc[i]["episode_admission_uid"],    ## dfepisode.iloc[i]["patient_site_uid"]                                   
                                                              
                                                                                  
                           "class": {"system": "http://terminology.hi17.org/CodeSystem/v3-ActCode",
                                                                            
                                      "code": "IMP",
                                      "display": dfepisode.iloc[i]["episode_description"]},
                                      
                           
                           "subject":{"reference": str(dfepisode.iloc[i]["patient_site_uid"])},
                           
                           
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
 

## Call the function to create the required json structure using
## dictionary.


dictJsonEpi = epi_dic_json(dfEpi)

## dictJsonEpi["17808"] #check
       


## Create the json file.

with open(pathofEpiJsonfile, 'w') as epiFjson:
    

    
    js.dump(dictJsonEpi,epiFjson)
    
    
