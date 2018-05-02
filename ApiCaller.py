import base64
import requests
import datetime
import boto3

def get_search_params(tickers):
          to_return = []
          for entry in tickers:
              search_params = {
                  'q': entry,
                  'count': 20,
                  'result_type': 'recent'
              }
              to_return.append(search_params)
          
          return to_return

def upload_to_s3(fileName):
          s3 = boto3.client('s3')
          s3.create_bucket(Bucket="jcox-stock-bucket")
          s3.put_object(Bucket="jcox-stock-bucket", Key=fileName, Body=open(fileName, 'rb'), ContentType='.log')

if __name__ == '__main__':
          client_secret = 'Your_Key'
          client_key = 'Your_Key'

          key_secret = '{}:{}'.format(client_key, client_secret).encode('ascii')
          b64_encoded_key = base64.b64encode(key_secret)
          b64_encoded_key = b64_encoded_key.decode('ascii')

          base_url = "https://api.twitter.com/"
          auth_url = '{}oauth2/token'.format(base_url)

          auth_headers = {
             'Authorization': 'Basic {}'.format(b64_encoded_key),
             'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
          }

          auth_data = {
             'grant_type': 'client_credentials'
          }

          auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
          access_token = auth_resp.json()['access_token']
          
          #Create Ticker list
          ticker_list = ['$nvda', '$baba', '$ge']          
          params_list = get_search_params(ticker_list)
          
          search_headers = {
            'Authorization': 'Bearer {}'.format(access_token)    
          }

          search_url = '{}1.1/search/tweets.json'.format(base_url)

          response_list = []
          for entry in params_list:
              response_list.append(requests.get(search_url, headers=search_headers, params=entry))

          #Create a collection of gathered tweets
          collection_of_tweets = []
      
          for entry in response_list:
              stock_tweets =[]
              tweet_data = entry.json()
              for x in tweet_data['statuses']:
                  print(x['text'])
                  stock_tweets.append(x['user']['screen_name'] + " said: " + x['text'])
              collection_of_tweets.append(stock_tweets)
          print collection_of_tweets

          #Create a log
          #Log files will contain all tickers and be timestamped
          i = 0
          file_name = []
          for ticker in ticker_list:
              file_name.append(ticker + "-")
          file_name.append(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
          complete_file_name = ''.join(file_name)
          file = open(complete_file_name, "w")
          for stock in collection_of_tweets:
              file.write("----------"+ ticker_list[i] +"----------\n")
              for tweet in stock:
                  file.write(tweet.encode('utf8'))
              i = i + 1
          file.close()
          upload_to_s3(complete_file_name)
