import logging
import boto3
import botocore
from urllib.parse import unquote

def lambda_handler(event, context):
    records = event['Records'][0]
    s3_data = records['s3']
    bucket = s3_data['bucket']
    obj = s3_data['object']
    bucket_name = bucket['name']
    key_name_enconded = obj['key']
    key_name_decoded = unquote(key_name_enconded)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(bucket_name)
    logger.info(key_name_decoded)
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket_name).download_file(key_name_decoded, 'my_local.txt')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
    else:
        raise
    # TODO implement
    return 'Hello from Lambda'
