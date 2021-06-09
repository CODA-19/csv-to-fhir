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
    
   
    
   sboto = boto3.resource('s3',aws_access_key_id = 'secret', aws_secret_access_key = 'secret', endpoint_url='http://recherche-coda19-rouge:9000',\
                   config=Config(signature_version='s3v4'))
   
   
   return sboto
    



def upload_file_minio(s3,filename):

   """
    
     This method uploads a file to a specified bucket in the Minio
     
     It is assumed here that the Minio has a bucket by the name
     chumtestbucket. Plus the file to be fetched and uploaded will
     have the names filename, and filename
     respectively (same names)
     
     It is assumed here that the file that is being fetched is in the working
     directory of the user.
     
     The location of the file in the Minio would be chumtestbucket/filename
     in the present case.
     
     Input argument: s3 type object
                     filename type string
     Return: None.

   """

   s3.Bucket('chumtestbucket').upload_file(filename,filename)


    


def create_presigned_url(bucket_name, object_name, expiration=3600):
   
    """
     Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    
    
    Kept the connection separate here.
    
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3', endpoint_url='http://recherche-coda19-rouge:9000',aws_access_key_id = 'secret', aws_secret_access_key = 'secret')
    
    try:
        response = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name,'Key': object_name}, ExpiresIn=expiration)
    
    except ClientError as e:
    
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response




def remove_file(s3, filetoremove):
    
    
    """
    
    This file will remove a specified file from the
    bucket chumtestbucket
    
    Input argument: s3 type object
                    filetoremove type string
                    
    Return:  obj_to_delete type object              
    
    
    """
    
    
    obj_to_delete = s3.Object('chumtestbucket', filetoremove)
    
    return obj_to_delete




# Program entry
if __name__ == "__main__":
    
    
    
    ## File to upload and file to remove
    ## specify your file here.
    
    filetoupload = 'abc.ndjson.gz'
    filetoremove = 'abc.ndjson.gz'
    
    
    ## Establish the connection with Minio 
    
    s3 = establish_minio_connect()
    
    
    ## Upload files to the Minio
    
    upload_file_minio(s3, filetoupload)
    
    
    ## Call the create url function by providing the name of the bucket in Minio and the desired
    ## file.
    
    url = create_presigned_url('chumtestbucket', filetoupload)
    
    ## Create the payload
    
    payload=({"source":url})
    
    
    ## Perform the user authorization
    ## Basic authorization settings described by python_load_script was performed earlier in the Aidbox.
    ## To nkow more refer to https://docs.aidbox.app/user-management-1/auth/basic-auth
    
    requests.get("http://recherche-coda19-orange:8888/User", auth=requests.auth.HTTPBasicAuth('python_load_script','chum123'))
    
    
    ## Perform the upload task to the Aidbox.
    
    requests.post("http://recherche-coda19-orange:8888/$load",auth=requests.auth.HTTPBasicAuth('python_load_script','chum123'),json=payload)
    
    
    
    ## Remove file from the Minio bucket
    
    checkremove = remove_file(s3, filetoremove)
    
    
    
    
    