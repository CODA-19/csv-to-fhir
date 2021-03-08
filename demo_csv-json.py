#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 21:17:39 2020

This program reads the relevant csv files and then creates
a json file using the data retrieved based on the FHIR
structure.


@author: rdas
"""

import numpy as np
import pandas as pd
import json as js
import csv as cv


## Define the paths (The paths here are those that considered the CITADEL infrastructure)

#pathOfPatientfile = '/data8/projets/Mila_covid19/output/covidb_full/csv/patient_data.csv'


pathOfPatientfile = '/data8/network_mount/S/CODA19_Anon_csv/patient_data_birthdate.csv'
pathofDemoJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Nov_17/demographic_data.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.


dfDemo = pd.read_csv(pathOfPatientfile)



def dem_dic_json(dfDemodata):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfDemodata type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    
    
    
    
    """
    
   
    
    dict_json = {}
    
    for i in range(len(dfDemodata)):
        
        ## Initialize the deceased flag as true
        ## Then check the patient is dead or alive.
        
        #setdeceasedFlag = 'true'
        
        #if(dfDemodata.iloc[i]["patient_vital_status"] == 'alive'):
            
        #    setdeceasedFlag = 'false'
        
        
        
        ## This is done to have only the first day of the month
        ## in the time stamp.
        
        datetime_string = dfDemodata.iloc[i]["patient_birth_date"]
        datetime_list = list(datetime_string)
        datetime_list[8]='0'
        datetime_list[9]='1'
        
        
        
        datetime_input = ''.join(datetime_list)
        
        single_json = { 
                
                
                           # The type of resource
                           
                           "resourceType" : "Patient",                                                  
                           
                           # Each resource entry has a unique id. This needs to be present for the bulk import to Aidbox to work
                           
                           "id": dfDemodata.iloc[i]["patient_site_uid"],
                            
                          
                           # The gender of the individual: male | female | other | unknown 
                            
                           "gender" :  dfDemodata.iloc[i]["patient_sex"],                                  
                                                        
                            
                           # The date of birth of the individual (YYYY-MM-DD)                            
                             
                           "birthDate" : datetime_input,   
                           
                           
                           # Indicates if the individual is deceased or not.
                           
                           #"deceasedBoolean" : setdeceasedFlag,
                           
                           # Time of death, if applicable (YYYY-MM-DDThh:mm:ss+zz:zz)       
                           
                           #"deceasedDateTime" : "YYYY-MM-DDThh:mm:ss+zz:zz",
                                     
                       }


        dict_json.update({str(i) : single_json})
        
        
    return(dict_json)    
        
        
    


## Replace patient_birth_date that are empty with 0000-00-00 00:00:00 to avoid issues later.

dfDemo['patient_birth_date'].fillna('0000-00-00 00:00:00', inplace = True)




## Call the function to create the required json structure using
## dictionary.


dictJsonDemo = dem_dic_json(dfDemo)    


# ## Create the json file.

with open(pathofDemoJsonfile, 'w') as demoFjson:
    
    
     js.dump(dictJsonDemo,demoFjson)
