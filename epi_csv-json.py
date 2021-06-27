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
import json
import datetime
from datetime import date


## Define the paths (The paths here are those that considered the CITADEL infrastructure)




#pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/april_16_data/episode_data.csv'
#pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Apr_16/episode_data.json'


pathOfEpifile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/episode_data.csv'
pathofEpiJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/episode_data.json'


path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'




# Read the location json file

with open("location.json","r") as f:

     location_dict = json.load(f)



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





def process_epi_df(dfEpitoprocess):
    
      
    ## An extra field is being added here to the data frame which would be used later to 
    ## store flag whether the row would be used or not in the json
    
    dfEpitoprocess['considered'] = 0
    
    
    
    ## Initiate the episode dataframe processing to consider the array of location case.
    
    for i in range(len(dfEpitoprocess)):
        
        
        
        ## If the row has not been considered so far then do
        
        if(dfEpitoprocess.loc[i,'considered'] == 0):
            
            
            ## Pick the admission uid
            
            admId = dfEpitoprocess.loc[i,'episode_admission_uid']
            
        else:
            
            continue
        
        
        ## Consider all the indices that are associated with the admission uid
        
        rowsReturned = dfEpitoprocess[dfEpitoprocess['episode_admission_uid']== admId].index
        
        
        ## If the number of indices is more than one then do
        
        if(len(rowsReturned) > 1):
            
            
            strunit_type = ''
            strstart_time = ''
            strend_time = ''
            
            counterFalg = 0 
            
            for j in rowsReturned:
                
                if counterFalg == 0:
                    
                   strunit_type = dfEpitoprocess.loc[j,'episode_unit_type']          
                   strstart_time = dfEpitoprocess.loc[j,'episode_start_time']
                   strend_time = dfEpitoprocess.loc[j,'episode_end_time'] 
            
                   counterFalg = counterFalg + 1    
            
                else:
                    
                   ## After constructing different strings, these rows would be
                   ## dropped.
                    
                   strunit_type = strunit_type +  ',' + dfEpitoprocess.loc[j,'episode_unit_type']          
                   strstart_time = strstart_time + ',' + str(dfEpitoprocess.loc[j,'episode_start_time']) ## Some are float which is strange
                   strend_time = strend_time  + ',' + str(dfEpitoprocess.loc[j,'episode_end_time']) ## Some are float which is strange
                   dfEpitoprocess.loc[j,'considered'] = 1
                   
                   
                   counterFalg = counterFalg + 1
                   
                
                ## Once the strings are complete it is assigned to the first row index
                   
                dfEpitoprocess.loc[rowsReturned[0],'episode_unit_type'] = strunit_type
                dfEpitoprocess.loc[rowsReturned[0],'episode_start_time'] = strstart_time
                dfEpitoprocess.loc[rowsReturned[0],'episode_end_time'] = strend_time   
                    
    
    
    ## Only take those rows that have the  flag set as 0
    
    dfmodifiedEpi = dfEpitoprocess[dfEpitoprocess["considered"]==0]

    return dfmodifiedEpi




    
    
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
            display_complete_input = ''
            
            
            
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
                   display_complete_input = ''                
          
                 
        
        single_json = { 
                
                
                           "resourceType" : "Encounter",
                           
                           "id": dfepisode.iloc[i]["episode_admission_uid"],    ## dfepisode.iloc[i]["patient_site_uid"]                                   
                               
                           
                           ## One of https://www.hl7.org/fhir/valueset-encounter-status.html
                           ## planned, arrived, triaged, in-progress, cancelled, unknown
                                                      
                           "status": "finished",
                           
                                                                                  
                           "class": {
                                         "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                                         "code": 'IMP',                         
                                         "display": dfepisode.iloc[i]["episode_description"]},        
                                      
                           
                           "subject":{"reference": 'Patient' + '/' + str(dfepisode.iloc[i]["patient_site_uid"])},
 
    
## To accomodate array for all loactions associated with the encounter
                          
#                           "location": [ { 
#                                                                            
#                                         "location":{ 
#                                         
#                                         "system": 'https://www.hl7.org/fhir/v3/ServiceDeliveryLocationRoleType/vs.html',        
#                                         "reference": 'Location' + '/' + str(location_dict[code_input]),
#                                         "display":  display_complete_input
#                                         
#                                       },
#                                   
#                                       "status": "completed",
#                                       
#                                       "period": {
#                                                  "start": dfepisode.iloc[i]["episode_start_time"],
#                                                  "end": dfepisode.iloc[i]["episode_end_time"]
#                                                  }
#                                       
#                                       }
#                                   
#                                   ],                  
                           
                        
                            
                                                     
#                           "period": {"start":  dfepisode.iloc[i]["episode_start_time"] ,
#                                        "end": dfepisode.iloc[i]["episode_end_time"] }
                           
## To accomodate array for all loactions associated with the encounter                              
                           
                           
                             "period": {"start": (datetime.datetime.strptime(min(str(dfepisode.iloc[i]["episode_start_time"]).split(',')),'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ') ,
                                        "end": (datetime.datetime.strptime(max(str(dfepisode.iloc[i]["episode_end_time"]).split(',')),'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ')}
                                                
                       }
                           
        
        ## The following lines except the json update were added to consider cases where there could be multiple locations associated 
        ## with an encounter. 
                   
                           
        single_json["location"] = []                   
                           
        element_count = dfepisode.iloc[i]["episode_unit_type"].split(",")

        for m in range(len(element_count)):

          for k in range(len(dic_chum["unitType"])):

             string_check = dic_chum["unitType"][k]['display_string'][:5]

             if(string_check == (dfepisode.iloc[i]["episode_unit_type"].split(",")[m][:5])):

                    #system_input = dic_chum["unitType"][k]['fhir_reference_url']
                    code_input = dic_chum["unitType"][k]['fhir_code']   
                    display_complete_input = dic_chum["unitType"][k]['display_string']
                    
                    episode_start =  (datetime.datetime.strptime(str(dfepisode.iloc[i]["episode_start_time"]).split(",")[m],'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ')
                    episode_end =  (datetime.datetime.strptime(str(dfepisode.iloc[i]["episode_end_time"]).split(",")[m],'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ')
                    
                    single_json["location"].append({"location":{"reference" : 'Location' + '/' + \
                               str(location_dict[code_input]), "display" : display_complete_input},  "status": "completed", \
                               "period":{"start":episode_start,"end":episode_end}})
                                         
                           
                    break       
    
        dict_json.update({str(i) : single_json})
    
        
    
    return(dict_json)
 




## load the dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 


## Fill the missing episode_unit_type with unknown.

dfEpi['episode_unit_type'].fillna('unknown', inplace = True)


## Replace episode_description that are na  with "" to avoid issues later.

dfEpi['episode_description'].fillna('', inplace = True)

## To deal with the issue of date time field when empty/na.

dfEpi['episode_start_time'].fillna('1900-01-01 00:00:00', inplace = True)
dfEpi['episode_end_time'].fillna('1900-01-01 00:00:00', inplace = True)


## Process the dataframe for location merger.

dfEpi_forlocation = process_epi_df(dfEpi)



## Call the function to create the required json structure using
## dictionary.


dictJsonEpi = epi_dic_json(dfEpi_forlocation,dict_data)

## dictJsonEpi["17808"] #check
       


## Create the json file.

with open(pathofEpiJsonfile, 'w') as epiFjson:
    

    
    js.dump(dictJsonEpi,epiFjson)
    
    
