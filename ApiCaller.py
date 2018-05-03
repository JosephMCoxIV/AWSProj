import base64
import requests
import datetime
import boto3
import time

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

def get_twitter_data(user_tracker):
          client_secret = 'OHF9BIXYQi9WbDUpaORU6mc1aPQPFgTRwz9ZGG1o4Sugpqumcq'
          client_key = 'gCDZOmD6qJXeYeL8qwWMPXaW4'
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
          i = 0
          new_entries = 0
      
          for entry in response_list:
              stock_tweets =[]
              tweet_data = entry.json()
              for x in tweet_data['statuses']:
                  print(x['user']['screen_name']+" said "+ x['text']+"\n")
                  #Get the user who created the tweet, as well as the stock ticker he is talking about
                  user = x['user']['screen_name'] + x['text'] + ticker_list[i]
                  if user in user_tracker:
                      new_entries = 1 
                  else:
                      user_tracker[user] = "Added"
                      print("Adding new person")
                      stock_tweets.append(x['user']['screen_name'] + " said: " + x['text'])
              collection_of_tweets.append(stock_tweets)
              i = i + 1

          #Create a log
          #Log files will contain all tickers and be timestamped
          i = 0
          file_name = []
          file_name.append(datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S"))
          file_name.append(".log")
          complete_file_name = ''.join(file_name)
          complete_file_name = complete_file_name.replace("$","")
          #file = open(complete_file_name, "w")
          file_name_collection = [] 
          for stock in collection_of_tweets:
              file_name_for_stock = []
              file_name_for_stock.append(ticker_list[i].replace("$",""))
              file_name_for_stock.append(complete_file_name)
              file_name = ''.join(file_name_for_stock)
              file_name_collection.append(file_name)
              file = open(file_name,"w")
              file.write("----------"+ ticker_list[i] +"----------\n")
              for tweet in stock:
                  file.write(tweet.encode('utf8')+ "\n")
              i = i + 1
              file.close()
          for name in file_name_collection:
              upload_to_s3(name)

if __name__ == '__main__':
          start_time = time.time()
          user_tracker = {}
          while True:
              get_twitter_data(user_tracker)
              print("Iteration Complete\n")
              time.sleep(60.0 - ((time.time() - start_time) % 60))
