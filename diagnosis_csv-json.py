#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:25:42 2020


This program reads  the relevant csv files and then creates
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
import datetime
from datetime import date
import dateutil.parser as parser 


## Define the paths (The paths here are those that considered the CITADEL infrastructure)



pathOfDiagnosisfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/diagnosis_data.csv'
pathOfPatientfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/patient_data.csv'

pathofDiagnosisJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/diagnosis_data.json'
path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/chum.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfDiagnosis = pd.read_csv(pathOfDiagnosisfile)


dfDemo = pd.read_csv(pathOfPatientfile)







def calculate_age(born, detecteddate):
    
    
    """
    
    This method calculates the age of the patient
    when an ailment was first detected. 
    
    Input arguments: born    :datetime object
                     detecteddate : datetime
    
    
    Returns:
        
            Age: int
    
    """
    
    
    
    try:
       
        birthday = born.replace(year = detecteddate.year)
            
        
    except ValueError:
        
        birthday = born.replace(year = detecteddate.year, month = born.month + 1, day=1)

    if birthday > born:
        
        return detecteddate.year - born.year - 1
    
    else:
        
        return detecteddate.year - born.year
        



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






def diagnosis_dic_json(dfDiagnosis, dfPatient):
    
    
        
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfDiagnosis type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
   
    
    for i in range(len(dfDiagnosis)):
    
        
        
        # Pick the patient uid from the diagnosis data and find the relevant data
        # in the patient table, such as the birthdate.
        
        check_patient_uid = dfDiagnosis.iloc[i]["patient_site_uid"]        
        index_of_interest = dfPatient.index[dfPatient.patient_site_uid == check_patient_uid]
        
        
        # The diagnosis date and time.
        
        diagnosis_date = datetime.datetime.strptime(dfDiagnosis.iloc[i]["diagnosis_time"],'%Y-%m-%d %H:%M:%S')
        
         
        # Calculate the age when the problem was diagnosed.
    
        patientage = calculate_age(datetime.datetime.strptime(dfDemo["patient_birth_date"][index_of_interest[0]],'%Y-%m-%d'),diagnosis_date)

        single_json = { 
                             
                            # The type of resource
                
                            "resourceType": "Condition",
                            
                            # Each resource entry needs a unique id for the ndjson bulk upload
                            
                            "id": dfDiagnosis.iloc[i]["diagnosis_uid"],
                            
                                             
                           
                            "subject": {
                                 
                               "reference": 'Patient' + '/' + str(dfDiagnosis.iloc[i]["patient_site_uid"])
                            },
                          

                            # Clinical episode associated with the observation (if possible)
                            
                            "encounter": {"reference": "Encounter/2314234"},

                      
                            "onsetDateTime": (datetime.datetime.strptime(dfDiagnosis.iloc[1]["diagnosis_time"],'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ'),
                          
                            
                            # Age at which the Condition began to occur
                            # Precalculated with birthDate (Resource/Patient)
                            
#                            "onsetAge": {
#                            
#                                "value": patientage,
#                                "unit": "years",
#                                "system": "https://ucum.org/ucum.html",
#                                "code": "a"
#                              },
                            
                          
                            "code": {
                              
                              "coding": [
                                                                           
                                  {
                            				#"system": "http://hl7.org/fhir/ValueSet/icd-10",
                                        "system": "http://hl7.org/fhir/sid/icd-10",
                            				"code": dfDiagnosis.iloc[i]["diagnosis_icd_code"],
                            				"display": dfDiagnosis.iloc[i]["diagnosis_name"]
                            		 }
                               
                                ],
                               
                                "text": dfDiagnosis.iloc[i]["diagnosis_name"]
                                                      
                                  
                            }                
                                                               
                                          
                          
                      }
                       
        dict_json.update({str(i) : single_json}) 

    return(dict_json)   




## For cases where the entries are -01

dfDemo['patient_birth_date'] = dfDemo['patient_birth_date'].replace({'-01':'1900-01-01'})



## Call the function to create the required json structure using
## dictionary.


dictJsonDiagnosis = diagnosis_dic_json(dfDiagnosis, dfDemo)    


## Create the json file.

with open(pathofDiagnosisJsonfile, 'w') as diagnosisFjson:
    
    
    js.dump(dictJsonDiagnosis,diagnosisFjson)           
