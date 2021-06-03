#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 17:29:17 2021

This script uploads a file from the bucket of Minio to Aidbox by using the location url.

The program can be placed under a crontab scheduler for automation.



@author: rdas


"""



import os
import requests
import requests.auth
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging 




def establish_minio_connect():
    
   """
    
    This method establishes the connection with Minio through the use
    of boto3.
    
    aws_access_key_id = "From the Minio key file (secret)"
    aws_secret_access_key = "From the Minio key file (secret)"
    
   """
    
   
    
   sboto = boto3.resource('s3',aws_access_key_id = 'secret', aws_secret_access_key = 'secret', endpoint_url='http://recherche-coda19-orange:9000',\
                   config=Config(signature_version='s3v4'))
   
   
   return sboto
    
    


def create_presigned_url(bucket_name, object_name, expiration=3600):
   
    """
     Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', endpoint_url='http://recherche-coda19-orange:9000',aws_access_key_id = 'secret', aws_secret_access_key = 'secret')
    
    try:
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name,'Key': object_name}, ExpiresIn=expiration)
    
    except ClientError as e:
    
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response



# Program entry
if __name__ == "__main__":
    
    
    
    ## Establish the connection with Minio (not required here)
    
    # s3 = establish_minio_connect()
    
    ## Call the create url function by providing the name of the bucket in Minio and the desired
    ## file.
    
    url = create_presigned_url('chumtestbucket', 'culture_data.json.ndjson.gz')
    
    ## Create the payload
    
    payload=({"source":url})
    
    
    ## Perform the user authorization
    ## Basic authorization settings described by python_load_script was performed earlier in the Aidbox.
    ## To nkow more refer to https://docs.aidbox.app/user-management-1/auth/basic-auth
    
    requests.get("http://recherche-coda19-orange:8888/User", auth=requests.auth.HTTPBasicAuth('python_load_script','chum123'))
    
    
    ## Perform the upload task to the Aidbox.
    
    requests.post("http://recherche-coda19-orange:8888/$load",auth=requests.auth.HTTPBasicAuth('python_load_script','chum123'),json=payload)
    
    
    
    
    