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
import datetime 


## Define the paths (The paths here are those that considered the CITADEL infrastructure)


#pathOfPatientfile = '/data8/network_mount/S/CODA19_Anon_csv/april_16_data/patient_data.csv'
#pathOfDiagnosisfile = '/data8/network_mount/S/CODA19_Anon_csv/april_16_data/diagnosis_data.csv'
#pathofDemoJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files_Apr_16/demographic_data.json'



pathOfPatientfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/patient_data.csv'
pathOfDiagnosisfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/diagnosis_data.csv'
pathofDemoJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/demographic_data.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.


dfDemo = pd.read_csv(pathOfPatientfile)

dfDiagnosis = pd.read_csv(pathOfDiagnosisfile)


## Select only those from the diagnosis list that comprise
## information concerning death.

dfDiagnosis_dead = dfDiagnosis[dfDiagnosis.diagnosis_name == 'death']



## The following lines try to mimic joins used in sql queries. The first (commented section) lists
## patients who are dead due to covid. The second incorporates an approach that considers all
## possible deaths not just due to covid.


#returnCovid_dead = dfDiagnosis_dead.merge(dfDemo[dfDemo.patient_covid_status == 'positive'][['patient_site_uid']], \
#                               left_on = 'patient_site_uid', right_on = 'patient_site_uid', how='inner')[['patient_site_uid', \
#                                     'diagnosis_name','diagnosis_time']]



returnCovid_dead = dfDiagnosis_dead.merge(dfDemo[['patient_site_uid']], \
                               left_on = 'patient_site_uid', right_on = 'patient_site_uid', how='inner')[['patient_site_uid', \
                                     'diagnosis_name','diagnosis_time']]





def dem_dic_json(dfDemodata,dfcovid_dead):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfDemodata type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    
    
    
    
    """
    
   
    
    dict_json = {}
    
    for i in range(len(dfDemodata)):
        
        ## Initialize the deceased flag as 0
        ## Initialize the time of death as '0000-00-00 00:00:00.
        
        setdeceasedFlag = 'false'
        
        #timeofdeath = '0000-00-00 00:00:00'
        timeofdeath = 'null'
          
               
        sexdetail = 'unknown'
        
        patient_uid_check = dfDemodata.iloc[i]["patient_site_uid"]
        
        
        ## Check whether the patient is dead or not. If yes set the flag and the
        ## relevant details accordingly.
        
        matchIndex = dfcovid_dead.index[dfcovid_dead.patient_site_uid == patient_uid_check]
        
        if(len(matchIndex)>0):
            
            setdeceasedFlag = 'true'

            timeofdeath =  dfcovid_dead.iloc[matchIndex[0]]["diagnosis_time"]
                    
                    
                   
        

        if(dfDemodata.iloc[i]["patient_sex"] == 'male'):
            
            sexdetail = 'male'
            
        elif(dfDemodata.iloc[i]["patient_sex"] == 'female'):
            
            sexdetail = 'female'
        
        
        ## This is done to have only the first day of the month
        ## in the time stamp.
        
        datetime_string = dfDemodata.iloc[i]["patient_birth_date"]
        datetime_list = list(datetime_string)
        #datetime_list[8]='0'
        #datetime_list[9]='1'
        datetime_list = datetime_list[0:7]
                
        
        
        datetime_input = ''.join(datetime_list)
        
        
        
        single_json = { 
                
                
                           # The type of resource
                           
                           "resourceType" : "Patient",                                                  
                           
                           # Each resource entry has a unique id. This needs to be present for the bulk import to Aidbox to work
                           
                           "id": dfDemodata.iloc[i]["patient_site_uid"],
                            
                          
                           # The gender of the individual: male | female | other | unknown 
                            
                           "gender" :  sexdetail,                                  
                                                        
                            
                           # The date of birth of the individual (YYYY-MM-DD)                            
                             
                           "birthDate" : datetime_input,   
                           
                           
                           # Indicates if the individual is deceased or not.
                           
                           "deceasedBoolean" : setdeceasedFlag,
                           
                           # Time of death, if applicable (YYYY-MM-DDThh:mm:ss+zz:zz)       
                           
                           "deceasedDateTime" : timeofdeath,
                                     
                       }


        dict_json.update({str(i) : single_json})
        
        
    return(dict_json)    
        
     
    
## To fix the issue when gender is empty.    
    
dfDemo['patient_sex'].fillna('', inplace = True)

## Replace patient_birth_date that are empty with 0000-00-00 00:00:00 to avoid issues later.

dfDemo['patient_birth_date'].fillna('0000-00-00 00:00:00', inplace = True)


## For cases where the entries are -01

dfDemo['patient_birth_date'] = dfDemo['patient_birth_date'].replace({'-01':'0000-00-00 00:00:00'})




## Call the function to create the required json structure using
## dictionary.


dictJsonDemo = dem_dic_json(dfDemo,returnCovid_dead)    


# ## Create the json file.

with open(pathofDemoJsonfile, 'w') as demoFjson:
    
    
     js.dump(dictJsonDemo,demoFjson)
