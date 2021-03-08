#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 01:46:30 2020


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



pathOfImagingfile = '/data8/network_mount/S/CODA19_Anon_csv/imaging_data.csv'
pathofImagingJsonfile = '/data8/network_mount/S/FHIR_json/Final_Oct_21/imaging_data.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfImaging = pd.read_csv(pathOfImagingfile)



def imaging_dic_json(dfImaging):
    
    
        
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: dfImaging type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    """
    
    
    
    dict_json = {}
   
    
    for i in range(len(dfImaging)):
    
    
    
        single_json = { 
                          
                          # The type of resource 
                          
                          "resourceType": "ImagingStudy",
                          
                          # Each resource entry needs a unique id for the ndjson bulk upload. 
                          
                          "id": dfImaging.iloc[i]["imaging_uid"], ## "patient_site_uid"
                          
     
                          "subject": {
                            "reference": "Patient/patid"
                          },
                          
                          
                                  
                          # YYYY-MM-DDThh:mm:ss+zz:zz        
                          
                          "started": dfImaging.iloc[i]["imaging_acquisition_time"],
                          
                          
                          "numberOfSeries": 1,
                          "numberOfInstances": 1,
                          
                          "procedureCode": [{
                              
                                 # Ref: http://playbook.radlex.org/playbook/SearchRadlexAction
                               
                                 "coding": [{
                                 "system": "http://www.radlex.org",
                                 "code": "RPID16",
                                 "display": "CT Chest wo IV Contrast"
                                 }],
  
                            "text": "CT Chest wo IV Contrast"
                         }],
                          
                                        
                          
                         "series": [
                            {
                              "uid": "2.16.124.113543.6003.2588828330.45298.17418.2723805630",
                              "number": 3,
                              "modality": {
                                "system": "http://dicom.nema.org/resources/ontology/DCM",
                                "code": dfImaging.iloc[i]["imaging_modality"]
                              },
                                      
                              "description": "CT Surview 180",
                              "numberOfInstances": 1,
                              "bodySite": {
                                "system": "http://snomed.info/sct",
                                "code": "67734004",
                                "display": dfImaging.iloc[i]["imaging_body_site"]
                              },
                              
                              "instance": [
                                {
                                  "uid": "2.16.124.113543.6003.189642796.63084.16748.2599092903",
                                  "sopClass": {
                                    "system": "urn:ietf:rfc:3986",
                                    "code": "urn:oid:1.2.840.10008.5.1.4.1.1.2"
                                  },
                                          
                                  "number": 1
                                  
                                }
                              ]
                            }
                          ]
                      }
                       
        dict_json.update({str(i) : single_json})
       
    
    
    return(dict_json)   
    
    
## Call the function to create the required json structure using
## dictionary.


dictJsonImaging = imaging_dic_json(dfImaging)    


## Create the json file.

with open(pathofImagingJsonfile, 'w') as imagingFjson:
    
    
    js.dump(dictJsonImaging,imagingFjson)        