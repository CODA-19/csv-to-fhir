#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 13:22:01 2020

This program reads the relevant csv files and then creates
a json file using the data retrieved based on the FHIR
structure.


@author: jplantin
"""


import pandas as pd
from datetime import datetime as dt
import json as js

#Define the paths (The paths here are those that considered the CITADEL infrastructure)

pathOfPatientFile = '/data8/projets/Mila_covid19/output/covidb_full/csv/intervention_data.csv'
pathOfInterJsonFile = '/data8/projets/Mila_covid19/data/S/FHIR_json/intervention_data.json'


## Load and process (if required) the data using Pandas and the csv file.
## Provides a dataframe.

dfInter = pd.read_csv(pathOfPatientFile)


def inter_dic_json(interData):
    
    """
    
    This function uses dictionary to create the structure
    required for the json file.
    
    Arguments:
        
        Input: interData type - dataframe (pandas)
        Returns :  dict_json  - type dictionary.
    
    
    
    
    
    """
    dict_json = {}
    
    for i in range(len(interData)):
        
        
                   
            setStatus = ""
            
            time = None
            
            
            if interData.iloc[i]["intervention_end_time"] == "NaT":
                
                setStatus = "Not completed"
                
            else:
                
                ## Converting string from dataframe to datetime.datetime class
                time = dt.strptime(interData.iloc[i]["intervention_end_time"], "%Y-%m-%d %H:%M:%S.%f")
                
                if time > dt.now():
                    
                ## To convert datetime.datetime class to string, if needed,
                ## remember to change the time argument inside the setStatus object.
                # strtime = dt.strftime(time,"%Y-%m-%d %H:%M:%S.%f")
                
                    setStatus = "Scheduled to be completed on {time}"
                
                else:
                
                    setStatus = "completed"


            

            # Set the "reference" value inside the "subject" key
            
            setPatientSiteUid = interData.iloc[i]["patient_site_uid"]
            strPatientSiteUid = str(setPatientSiteUid)
                         
            ## Set the "performedDateTime" value
            
            setPerfDateTime = interData.iloc[i]["intervention_start_time"]
           
                           
            single_json = {
                           
                            # The type of resource
                            
                            "resourceType": "Procedure",
                            
                            # Each resource entry needs a unique id for the ndjson bulk upload
                            
                            "id": "Provide id here",
                         
                           
                              
                            "subject": {
                               
                                    "reference": strPatientSiteUid
                              },
                            
                            
                            "code": {
                                "coding": [
                                  {
                                    "system": "http://snomed.info/sct",
                                    "code": "80146002",                                   
                                    "display": interData.iloc[i]["intervention_name"]
                                  }
                                ],
                                "text": "Appendectomy"
                              },
                              

                            "performedPeriod": {
                               # YYYY-MM-DDThh:mm:ss+zz:zz
                               "start": "2017-02-01T17:23:07Z",
                               "end": "2017-03-01T17:23:07Z"
                            },
                              
                              "status": setStatus, 
                         }
            
            dict_json.update({str(i) : single_json})
          
    return dict_json
                               
## Call the function to create the required json structure using
## dictionary.                          
        

dictJsonInter = inter_dic_json(dfInter)

##  Create the json file.

with open (pathOfInterJsonFile, "w") as InterFJson:
    
    js.dump(dictJsonInter, InterFJson)
    
