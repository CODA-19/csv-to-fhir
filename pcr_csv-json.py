#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 21:57:50 2020

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
import datetime
from datetime import date


## Define the paths (The paths here are those that considered the CITADEL infrastructure)


pathOfPcrfile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/pcr_data.csv'
pathofEpifile = '/data8/network_mount/S/CODA19_Anon_csv/encrypted_data/episode_data.csv'
pathofPcrJsonfile = '/data8/network_mount/S/FHIR_json/Mapped_Files/pcr_data.json'



path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/files_mapping/CHUM.json'



## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfPcr = pd.read_csv(pathOfPcrfile)

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



def pcr_raw_string_check(rawstring):
    
    
    """
    
    This method maps the entries present in the 
    Airtable to that present in the DB
    
    Arguments:
        
       rawstring: A string
       
       
    Returns:
        
       stringreturn: A string   
    
    
    """
    
    
    
    rawstringvalue = str(rawstring)
    
    if rawstringvalue == 'chlamydia':
        
       stringreturn = 'chlamydia'
        
    elif rawstringvalue =='covid':
                 
       stringreturn = 'sars_cov2'
                 
    elif rawstringvalue =='gonocoque':
        
       stringreturn = 'gonorrhea'
            
    elif rawstringvalue =='herpès':
          
       stringreturn =  'herpes_simplex_virus'         
        
    elif rawstringvalue =='influenza a':
             
        stringreturn = 'influenza_a'
        
    elif rawstringvalue =='influenza b':
        
       stringreturn = 'influenza_b'
               
    elif rawstringvalue =='l. monocytogenes':
                
       stringreturn = 'listeria_monocytogenes'
                
    elif rawstringvalue =='rsv':
                
       stringreturn = 'varicella_zoster_virus'
                
    elif rawstringvalue =='vbk':
                
       stringreturn = 'bk_virus'
                
    elif rawstringvalue =='virus jc':
                
       stringreturn = 'jc_virus'
                
    elif rawstringvalue =='vzv':
                
       stringreturn = 'varicella_zoster_virus'
       
              
    return stringreturn    
    
    
    
     




def pcr_dic_json(dfPcrData, dic_chum):
    
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    
    
    The script now also considers values from the airtable and compares
    them with the values in the dataframe(csv). If there is a match, then
    the values from the dictionary json (airtable) are inserted in the
    json created below.
    
    Arguments:
        
        Input: dfPcrData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
    
    for i in range(len(dfPcrData)):
        
        
        
        ## The default values.
        
        status_fhir = 'unknown'
        result_fhir = 'IND'   
        display_fhir = 'Indeterminate'
        
        
        ## Fetch the array/list name.
        
        key_exist = dic_chum.get("pcrResultStatus","None")
        
        
        #indexfor_episode = dfEpi[dfEpi['patient_site_uid']== dfPcr.iloc[i]["patient_site_uid"]].index
        
        #episode_uid = dfEpi.iloc[indexfor_episode[0]]['episode_admission_uid']
        
       
        
        
        if(key_exist == 'None'):
            
            
            system_input = 'http://snomed.info/sct'            
            code_input = ''                        
            display_complete_input = ''
            
            
            
        else:
            
            
            ## consider the dictionary/object in the json dictionary using the key and fetch
            ## the values. Here the first three characters are considered to perform a match
            ## check. In the present scenario this was a simpler approach.   
            
            
          for k in range(len(dic_chum["pcrResultStatus"])):   
            
                     
            string_check_raw = dic_chum["pcrResultStatus"][k]['raw_string_lower']  
            
            if(string_check_raw == 'négatif'):
                
             
               string_check = string_check_raw[:3].replace('é','e')
               
                              
            elif(string_check_raw == 'non détecté'): 
                
                string_check = 'neg'
                
            elif(string_check_raw == 'test annulé' or string_check_raw == 'annulé' or string_check_raw == 'non valide' \
                 or string_check_raw == 'en attente' or string_check_raw == 'rapp. numérisé'):  
                
                string_check = 'und' #Undetermined
                
            elif(string_check_raw == 'positif'):    
            
                
               string_check = 'pos' 
               
               
              
            if((string_check)==(dfPcrData.at[i,'pcr_result_value'][:3])):   #raw_string_lower  
              
              if('result_snomed_code'in dic_chum["pcrResultStatus"][k].keys()):
             
                system_input = dic_chum["pcrResultStatus"][k]['snomed_reference_url']            
                code_input = dic_chum["pcrResultStatus"][k]['result_snomed_code']                       
                display_complete_input = dic_chum["pcrResultStatus"][k]['raw_string_lower']
                status_fhir = dic_chum["pcrResultStatus"][k]['status_fhir_code']
                result_fhir = dic_chum["pcrResultStatus"][k]['result_fhir_code']
                display_fhir = dic_chum["pcrResultStatus"][k]['result_fhir_display_string']
        
                break
        
                
        ## Fetch the array/list name.
        
        key_exist_loinc = dic_chum.get("pcrName","None")

 
        if(key_exist_loinc == 'None'):
            
            
            system_input_loinc = 'http://loinc.org'            
            code_input_loinc = ''                        
            display_complete_input_loinc = ''
            
          
        else:   
                
          
          for k in range(len(dic_chum["pcrName"])):  
            
              
             airtable_entries_present = True 
              
             #if((dic_chum["pcrName"][k]['display_string'])==(dfPcrData.at[i,'pcr_name'])):   #raw_string_lower
             if(pcr_raw_string_check((dic_chum["pcrName"][k]['raw_string_lower']))==(dfPcrData.at[i,'pcr_name'])):
                 
              
                if('loinc_code'in dic_chum["pcrName"][k].keys()):
              
                  system_input_loinc = dic_chum["pcrName"][k]['loinc_reference_url']       # dic_chum["pcrName"][k]['loinc_reference_url']            
                  code_input_loinc = dic_chum["pcrName"][k]['loinc_code']                       
                  display_complete_input_loinc = dic_chum["pcrName"][k]['display_string']
                  
                  airtable_entries_present = False                         
                  
                  break
                  
                else:
                    
                                   
                  system_input_loinc = 'http://loinc.org'            
                  code_input_loinc = ''                       
                  display_complete_input_loinc = ''  
             
                  airtable_entries_present = True
                  
                 
                
             if(airtable_entries_present):
                
                 system_input_loinc = 'http://loinc.org'            
                 code_input_loinc = ''                       
                 display_complete_input_loinc = '' 
                 
       
        ## Garbage entries in the sample time were throwing errors
        ## to avoid this,if such a value is encountered it is replaced by the result time
        ## This may change (would be clarified later)
       
        try:
          
          issuedate = (datetime.datetime.strptime(dfPcr.iloc[i]["pcr_result_time"],'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ')
          
        except:
          
          issuedate = (datetime.datetime.strptime(dfPcr.iloc[i]["pcr_sample_time"],'%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        
        
        
        
        single_json = { 
                
                            # The type of resource
                            
                            "resourceType" : "Observation",
                           
                             # Each resource entry needs a unique id for the ndjson bulk upload.
                            
                            "id": dfPcrData.iloc[i]["pcr_uid"],

                             
                            # The status of the observation: registered | preliminary | final | amended 
                                                                         
                            #"status": dfPcrData.iloc[i]["pcr_result_status"],
                            
                            "status": status_fhir,
                            
                            # Time of the observation (YYYY-MM-DDThh:mm:ss+zz:zz)
                            
                            "effectiveDateTime" : (datetime.datetime.strptime(dfPcrData.iloc[i]["pcr_sample_time"],\
                                                                              '%Y-%m-%d %H:%M:%S')).strftime('%Y-%m-%dT%H:%M:%SZ'),
                            
                            # Patient associated with the observation
                            
                            "issued": issuedate,
                            
                            # This needs to be associated with patient_site_id (how we can join labs to the patient table)
                            
                            "subject" : {"reference" : "Patient" + '/' + str(dfPcrData.iloc[i]["patient_site_uid"])},
                            
                            # Clinical episode associated with the observation (if possible)
                            
                            #"encounter": {"reference": "Encounter/2314234"},
                            
                            # LOINC code for the observation that was made (LOINC "code" field to be omitted until coding/categorization completed)
                            
                            "code": {
                                    
                              "coding": [     
                                    
                                   { "system" : system_input_loinc,
                                     "code": code_input_loinc,
                                     "display": dfPcrData.iloc[i]["pcr_name"]   
                                     }
                            
                            ],
                            
                            "text": dfPcrData.iloc[i]["pcr_name"]
                            
                            },
                            
                            # SNOMED code for the body site used (SNOMED "code" field to be omitted until coding/categorization completed)
                            
                            "bodySite": {
                               
                               "coding": [ 
                                
                                {          "system": system_input ,
                                           "code" : code_input,
                                           "display": dfPcrData.iloc[i]["pcr_sample_type"]} # Check this
                                ]
                               
                               },
                            
                                    
                            
                            # Value and units of measure
                            
                           "interpretation": [{
                                            "coding": [
                                                    
                                                 {
                                                    "system": system_input,
                                                    "code": code_input,
                                                    "display": dfPcrData.iloc[i]["pcr_result_value"]
                                                  },
                                                 
                                                 
                                                 {
                                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation", 
                                                    "code": result_fhir,   
                                                    "display": display_fhir
                                                   
                                                 }
                                                 
                                                                                          
                                             ]
                                            }]
                                     
                                     
                       }
                        
        dict_json.update({str(i) : single_json})

    return(dict_json)
    




## load thw dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 


## debug

#for i in dict_data["pcrResultStatus"]: 
    
    #print(i)
 

## Replace pcr_name value that are empty with none.    
    
dfPcr['pcr_name'].fillna('None', inplace = True)    

## Replace pcr_result_value that are empty with none to avoid issues later.

dfPcr['pcr_result_value'].fillna('None', inplace = True)

## Call the function to create the required json structure using
## dictionary.

dictJsonPcr = pcr_dic_json(dfPcr, dict_data)    


## Create the json file.

with open(pathofPcrJsonfile, 'w') as pcrFjson:
    
    
    js.dump(dictJsonPcr,pcrFjson)
