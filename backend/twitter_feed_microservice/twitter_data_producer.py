from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import configparser
import time
configParser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)
access_token = configParser.get('twitter-token-config', 'access_token')
access_token_secret =  configParser.get('twitter-token-config', 'access_token_secret')
consumer_key = configParser.get('twitter-token-config', 'consumer_key')
consumer_secret = configParser.get('twitter-token-config', 'consumer_secret')

#print(access_token, access_token_secret, consumer_key, consumer_secret)
print("Starting the kafka producer")
class StdOutListener(StreamListener):
    def __init__(self):
        self.counter=1;
    def on_data(self, data):
        #print(len(data))
        jsonData={"x":self.counter,"y":len(data)}
        producer.send_messages("trump", str(jsonData).encode('utf-8'))
        #print (data)
        time.sleep(1)
        self.counter+=1
        return True
    def on_error(self, status):
        print (status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(track="trump")
