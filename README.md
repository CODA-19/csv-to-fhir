# CODA-19: CSV to FHIR and Automation

This repository contains scripts to generate FHIR resources from data in a tabular / relational format.

## In addition, this repository will also provide details of the automation approach, involving the following tasks:
  
   *a) Upload a file to a Minio bucket 
    b) Generate the url for the uploaded file
    c) using the url upload the file to an Aidbox 
    d) Remove the file from the Minio bucket.*
    
  To upload a file that is present in the bucket of Minio to the Aidbox, consider the script https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_aidbox.py, to
  explore more consider the approaches tried in jupyter https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_orange.ipynb
  To set authorization (this allows the Rest API to interact with the Aidbox), consider the description here https://www.youtube.com/watch?v=xWtNNi_Q-dU&t=3s&ab_channel=HealthSamurai Set the Client id and Client secret values (in the example script here, the first is set as python_load_script, and the later as chum123)

  For clarity, consider the script (https://github.com/CODA-19/csv-to-fhir/blob/master/upload_minio_aidbox.py). Assuming there is a bucket (container) by the name chumtestbucket   which contains a file (ndjson.gz file to upload). In order to create the corresponding URL that would point to the specific file, call the method create_presigned_url. Once     the URL is generated create the payload using the line payload=({"source":url}). Subsequently, access the Aidbox and perform the upload using the lines requests.get() and       requests.post(). 
    
    
## Scheduling with Crontab

Crontab provides a good option to schedule various tasks. To know more about Crontab consider (https://www.geeksforgeeks.org/crontab-in-linux-with-examples/). Users can specify the day and time for the execution of a specific script. In the present scenario, shell scripts are written for individual tasks and they are then executed sequentially according to the order. First, the csvs are created, the files are then encrypted, converted to FHIR-Json, subsequently converted to ndjson, and finally zipped. Therefore, there are five tasks and we write five different shell scripts (with .sh extension). A typical Crontab command scheduling the five tasks for execution on Saturdays at 7:00 PM would be represented in the following manner:

00 19 * * SAT /usr/sbin/runuser -l rxyz -c '/usr/local/sbin/generate_csv.sh' && '/usr/local/sbin/generate_encrypted.sh' && '/usr/local/sbin/generate_json.sh’ && '/usr/local/sbin/create_ndjson.sh’ && '/usr/local/sbin/ndjson_to_zip.sh’

Where rxyz is the user name, the shell script file names (with .sh) are self-explanatory. Users should verify how they have installed the packages and the path of their files. A shell script example that uses the Anaconda environment is presented here  https://github.com/CODA-19/csv-to-fhir/blob/master/cron_example_json.sh A native Python installation that does not involve Anaconda will not require the sourcing of Anaconda bashrc as performed in the given example. It depends on how the users configure and use the various packages in terms of the shell scripts for scheduling. For instance, consider the case described in https://github.com/CODA-19/csv-to-fhir/blob/master/cron_example_to_ndjson.sh. The last script does not even use Python.

In order to generate the different csv or json files, a simple approach would be to use a wrapper python script. Consider the json scenario, in the wrapper script (https://github.com/CODA-19/csv-to-fhir/blob/master/wrapper_json.py) all the programs developed for the various jsons are called/executed. The wrapper script ultimately goes inside a shell script.  
    
    
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
