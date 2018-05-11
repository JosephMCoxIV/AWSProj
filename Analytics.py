import boto3
import sys
import botocore
client = boto3.client('ses')
message = {'Body': {'Text': {'Data': 'This is my body'}, 'Html': {'Data': 'Since Joseph Cox tweeted positive news, I would recommend to hold.'}}, 'Subject': {'Data': 'This is a subject'}}
#client.send_email(Source='josephmanleycox@gmail.com', Destination={'ToAddresses':['josephmanleycox@gmail.com']}, Message=message)

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
        for entry in user_tweets:
            if i == 0:
                i = i + 1
                continue
            split_content = entry.split('USERNAME: ')
            if len(split_content) == 1:
                break
            user_name_tweet = split_content[1].split(" said: ")
            if "Joseph_Cox" in user_name_tweet[0]:
                 message = {'Body': {'Text': {'Data': 'This is my body'}, 'Html': {'Data': 'Since Joseph Cox tweeted positive news, I would recommend to hold. Here is what he said:\n'+user_name_tweet[1]}}, 'Subject': {'Data': 'This is a subject'}}
                 client.send_email(Source='josephmanleycox@gmail.com', Destination={'ToAddresses':['josephmanleycox@gmail.com']}, Message=message)
                 print "Message has been sent!"
            i = i + 1
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
    else:
        raise

if __name__ == '__main__':

    read_file("jcox-stock-bucket", sys.argv[1])
    pass
