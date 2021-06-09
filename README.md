# CODA-19: CSV to FHIR

This repository contains scripts to generate FHIR resources from data in a tabular / relational format.

# In addition this repository will also provide details of the automation approach, involving the following tasks:
  
   *a) Upload a file to a Minio bucket 
    b) Generate the url for the uploaded file
    c) using the url upload the file to an Aidbox 
    d) Remove the file from the Minio bucket.*
    
  To upload a file that is present in the bucket of Minio to the Aidbox, consider the script https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_aidbox.py, to
  explore more consider the approaches tried in jupyter https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_orange.ipynb
  To set authorization (this allows the Rest API to interact with the Aidbox), consider the description here https://www.youtube.com/watch?v=xWtNNi_Q-dU&t=3s&ab_channel=HealthSamurai Set the Client id and Client secret values (in the example script here, the first is set as python_load_script, and the later as chum123)

  For clarity, consider the script (https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_aidbox.py). Assuming there is a bucket (container) by the name chumtestbucket   which contains a file (ndjson.gz file to upload). In order to create the corresponding URL that would point to the specific file, call the method create_presigned_url. Once     the URL is generated create the payload using the line payload=({"source":url}). Subsequently, access the Aidbox and perform the upload using the lines requests.get() and       requests.post(). 
    
    

## Requirements

Python v3

## Install

In order to install, clone the repository:

```
git clone https://github.com/CODA-19/csv-to-fhir
cd csv-to-fhir
```

## Tests

Todo.

## Authors

Rajeev Das
