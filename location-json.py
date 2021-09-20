#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  3 00:59:03 2021


This script creates the json file that carries location details of a patient
entering CHUM. It provides the ward and bed information. 




@author: rdas
"""



import json as js
import pandas as pd
import os, binascii
from connect_postgres import connectDB_returnDF


id_bucket = []

bed_valuebucket = []

path_to_dictionary = '/data8/projets/ChasseM_CODA19_1014582/fhir/code/rdas/dev_2021/chum.json'
pathofbedLocJsonfile = '/data8/network_mount/S/FHIR_json/dev_test/loc_bed.json'
pathofwardLocJsonfile = '/data8/network_mount/S/FHIR_json/dev_test/loc_ward.json'


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



## load the CHUM dictionary
  
    
dict_data = read_dictionary(path_to_dictionary) 



## Fetch the bed data from the DB. Pass the 
## following query and a dataframe is returned.

query = 'select distinct litno,localno, unitesoinscode from dw_test.cichum_sejhosp_live order by unitesoinscode'
dfhosp = connectDB_returnDF(str(query))

## The following columns are added to the dataframe to help
## merge with another dataframe (Emergency + Hospital)

dfhosp.insert(0, 'cod_emplace', None)
dfhosp.insert(1, 'de1', None)



## Fetch the relevant data for emergency casses

query_er_raw = 'select distinct urg_ep.cod_emplace, civier.de1,sejurg.noadm, sejhosp.litno, sejhosp.localno, sejhosp.unitesoinscode,\
sejurg.dossier, sejurg.dhreadm,sejurg.dhredep,sejurg.servcode \
from \
 dw_test.orcl_cichum_sejurg_live as sejurg \
inner join \
 dw_test.cichum_sejhosp_live as sejhosp \
 on sejhosp.no_episod_is_prov = sejurg.noadm \
and sejhosp.no_episod_is_prov is not null \
left join \
(select urgchum_episode.cod_emplace, urgchum_episode.no_episod_is \
 from urgchum_episode)as urg_ep \
on sejurg.noadm = urg_ep.no_episod_is \
left join \
 (select urgchum_emp_civier.cod_emplace, urgchum_emp_civier.de1 \
  from urgchum_emp_civier)as civier \
on urg_ep.cod_emplace = civier.cod_emplace '




dfemr_raw = connectDB_returnDF(str(query_er_raw))


## Drop the columns that are not nescessary

dfemr_raw = dfemr_raw.drop(columns=['dossier','dhreadm','dhredep','servcode', 'noadm'])

## Tag the data frame with the flag ER

dfemr_raw['unitesoinscode']= 'ER'

frames = [dfhosp,dfemr_raw]


## Merge the two dataframes

dfmerge = pd.concat(frames)


def loc_dic_json(dfhosploc,dic_chum):

    
    """
    
     Method to generate the bed information json
     
     Argument:
             
             dfhosploc dataframe object
             dic_chum  dictionary object
    
    """
    
    
    
    bedNumber = ''
    wardNumber = ''
    wardbedNumber = ''
    fhircode = ''
    display_entire = ''
    lit = ''
    matchnotFound = True
    
    dict_json = {}
    
   
        
    for i in range(len(dfhosploc)):    
        
      
      matchnotFound = True  
        
        
      for j in range(len(dic_chum["unitType"])):
            
          
           wardNumber = dic_chum["unitType"][j]["raw_string_lower"].upper()
           codeCheck = (str(dfhosploc.iloc[i]["unitesoinscode"]).replace(" ","")).upper()
           
           #if codeCheck == 'ER':
               
           #    if dfhosploc.iloc[i]["cod_emplace"] is not None:
                   
           #        wardNumber = dfhosploc.iloc[i]["cod_emplace"]
                   
           #    else:
                   
           #        wardNumber = "NA"
           
           
                    
            
           if(codeCheck == dic_chum["unitType"][j]["raw_string_lower"].upper()):
                  
                  
                 bedNumber = str(dfhosploc.iloc[i]["localno"]).replace(" ","")
                 lit = str(dfhosploc.iloc[i]["litno"]).replace(" ","")
                 
                 #wardbedNumber = wardNumber + '-' + bedNumber
                 
                 bedlocation = bedNumber + '-' + lit
                 
                 
                 fhircode = str(dic_chum["unitType"][j]['fhir_code'])
                 display_entire = str(dic_chum["unitType"][j]['display_string'])
                 
                 
                 if codeCheck == 'ER':
                   
                   if dfhosploc.iloc[i]["cod_emplace"] is not None:
                       
                       #display_entire = dfhosploc.iloc[i]["de1"]
                       bedlocation = str(dfhosploc.iloc[i]["de1"]).replace(" ","") + '-' + lit
                       
                                             
                       
                   else:
                       
                       #display_entire = "NA"
                       
                       bedlocation = "NA"
                 
                 
                 
                 
                 bedNumber = ''
                 
                 #wardNumber = ''
                 lit = ''
                 
                 matchnotFound = False
                 
                 if  bedlocation not in bed_valuebucket:
                           
                     bed_valuebucket.append(bedlocation)
                           
                 else:
                     
                     matchnotFound = True
                 
                 
                 
                     
                 break 
                
      
       
      ## It was observed that some of the entries in the
      ## DB do not have a similar entity in the dictionary json
      ## This line avoid such entries.
        
      if(matchnotFound):
          
                    
          continue
           
          
                        
            
            
      single_json = { 
            
                        
                       ## The type of resource
               
                       "resourceType" : "Location",
                       
                       
                       ## Each resource entry has a unique id. This needs to be present for the bulk import to Aidbox to work
                       
                       "id": str(binascii.hexlify(os.urandom(64)).decode('utf-8')),                                    
                           
                       ## Identify the bed number
                       
                       "identifier": [
                        {
                          #"value": str(dic_chum["unitType"][i]['raw_string_lower'])
                          "value": bedlocation
                        }
                       ],
                        
                       
                       ## Locations on a bed-level basis
                       
                       "physicalType": {
                        "coding": [
                          {
                            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                            "code": "bd",
                            "display": "Bed"
                          }
                        ]
                       },
                       
                       ## Use the Airtable UnitType terminology tab to map to correct unit
                       ## Use coding system displayed here:
                       ## http://terminology.hl7.org/CodeSystem/v3-RoleCode
                       
                       "type": [
                            {
                              "coding": [
                                {
                                  "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                  "code": fhircode,
                                  "display": display_entire
                                }
                              ]
                           }
                       ],
                              
                       # Add reference to the ward Location resource
                       
                       "partOf" : { 
                           "reference": "Location" + '/' + str(wardNumber) 
                        } 
                        
                        
                                            
                   }
   
      dict_json.update({str(i) : single_json})  
      
      id_bucket.append(dict_json[str(i)]['id'])
      
    
     
          
    return(dict_json)    




def loc_ward_json(dfhosploc,dic_chum):

  
    """
   
     Method to generate the ward information json.
     
     Argument:
         
         dfhosploc dataframe object.
         dic_chum  dictionary object.
   
   
    """
           
    
    wardNumber = ''   
    fhircode = ''
    display_entire = ''    
    matchnotFound = True
        
    
    dict_json = {}
    
           
    for i in range(len(dfhosploc)):
    
        
       matchnotFound = True   
        
        
       for j in range(len(dic_chum["unitType"])):
            
          
           wardNumber = dic_chum["unitType"][j]["raw_string_lower"].upper()
           codeCheck = (str(dfhosploc.iloc[i]["unitesoinscode"]).replace(" ","")).upper()
                          
                                 
           if(codeCheck == dic_chum["unitType"][j]["raw_string_lower"].upper()):
               
               wardNumber = dic_chum["unitType"][j]["raw_string_lower"].upper()
               
              
               fhircode = str(dic_chum["unitType"][j]['fhir_code'])
               display_entire = str(dic_chum["unitType"][j]['display_string']) 
               
               
               
               matchnotFound = False
              
               
                
               bulkidImport = str(binascii.hexlify(os.urandom(64)).decode('utf-8'))
                
               if(bulkidImport in id_bucket):
                
                   bulkidImport = str(binascii.hexlify(os.urandom(64)).decode('utf-8'))
                   
                   id_bucket.append(bulkidImport)
                                              
                                
                              
               
               break
            
            
       if(matchnotFound):
          
                    
          continue     
            
            
               
               
       single_json = { 
            
                        
                       ## The type of resource
               
                       "resourceType" : "Location",
                       
                       
                       ## Each resource entry has a unique id. This needs to be present for the bulk import to Aidbox to work
                       
                       "id": bulkidImport,                                    
                           
                       ## Identify the bed number
                       
                       "identifier": [
                        {
                          #"value": str(dic_chum["unitType"][i]['raw_string_lower'])
                          "value": wardNumber
                        }
                       ],
                        
                       
                       ## Locations on a bed-level basis
                       
                       "physicalType": {
                        "coding": [
                          {
                            "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                            "code": "wa",
                            "display": "Ward"
                          }
                        ]
                       },
                       
                       ## Use the Airtable UnitType terminology tab to map to correct unit
                       ## Use coding system displayed here:
                       ## http://terminology.hl7.org/CodeSystem/v3-RoleCode
                       
                       "type": [
                            {
                              "coding": [
                                {
                                  "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                  "code": fhircode,
                                  "display": display_entire
                                }
                              ]
                           }
                       ]
                        
                                            
                   }
   
       dict_json.update({str(i) : single_json})     
               
    return(dict_json)







dfmerge['unitesoinscode'].fillna('', inplace = True)
dfmerge['localno'].fillna('', inplace = True)


## Call the function to create the required json structure using
## dictionary. This is for the bed section.


dictJsonLoc = loc_dic_json(dfmerge,dict_data)


## Create the json file.

with open(pathofbedLocJsonfile, 'w') as locFjson:
    
    
    js.dump(dictJsonLoc,locFjson)

    

           
        
dfmerge = dfmerge.unitesoinscode.unique() 

dfward = pd.DataFrame(dfmerge,columns=['unitesoinscode'])

dictJsonWard = loc_ward_json(dfward,dict_data)


## Create the json file. This is for the ward json.

with open(pathofwardLocJsonfile, 'w') as wardFjson:
    
    
    js.dump(dictJsonWard,wardFjson)
       
