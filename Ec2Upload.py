import boto3
import botocore
from boto3.dynamodb.conditions import Key
import sys

def read_file(bucket_name, key_name_decoded):
    dynamo = boto3.resource('dynamodb')
    #records = event['Records'][0]
    #s3_data = records['s3']
    #bucket = s3_data['bucket']
    #obj = s3_data['object']
    #bucket_name = bucket['name']
    #key_name_enconded = obj['key']
    #key_name_decoded = unquote(key_name_enconded)
    s3 = boto3.resource('s3')
    try:
        s3.Bucket(bucket_name).download_file(key_name_decoded, key_name_decoded)
        file_obj = open(key_name_decoded, "r")
        content = file_obj.read()
        user_tweets = content.split(":;:")
        i = 0
        table = dynamo.Table("TweetsBaba")
        for entry in user_tweets:
            print entry
            if i == 0:
                i = i + 1
                continue
            print entry
            split_content = entry.split('USERNAME: ')
            print len(split_content)
            if len(split_content) == 1:
                break
            user_name_tweet = split_content[1].split(" said: ")
            user_id = str(i) + key_name_decoded
            user = {'id': user_id, 'user' : user_name_tweet[0],'tweet' : user_name_tweet[1]}
            table.put_item(Item=user)
            i = i + 1
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
    else:
        raise

if __name__ == '__main__':
    
    read_file("jcox-stock-bucket", sys.argv[1])
    pass
