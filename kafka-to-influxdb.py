# Program to copy data from kafka producer and move to influxdb database.
# Following is the data being processed
'''
{
   "product": {
      "category": "clothing",
      "product_id": "444434",
      "product_name": "Red Hat Impact T-shirt"
   },
   "rating": 0,
   "timestamp": 1687336745669,
   "user": {
      "name": "Alison Silva",
      "browser": "Chrome",
      "region": "India",
      "customer_id": "asilva"
   },
   "review_text": "Excellent T-shirt",
   "score": 3,
   "response": "positive"
}
'''

from kafka.consumer import KafkaConsumer
from kafka.producer import KafkaProducer
from kafka.errors import KafkaError
from transformers import pipeline
import ssl
import json
import os
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from datetime import datetime
from ssl import SSLContext, PROTOCOL_TLSv1
from influxdb import InfluxDBClient
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WriteOptions
from dateutil import parser

'''
requirements.txt
kafka-python
transformers
torch
pytorch
influxdb
influxdb-client
'''

bucket = "globex-bucket"
org = "globex"
token = "2avH4WIAuQagJ_E5Q-SgA50x1K79IT5ruql27hH0bklvYZrrnKeuc3lvlvMx_SSvPwTlVe3chV66IcOUl43EaA=="
# Store the URL of your InfluxDB instance
url="http://influxdb-influxdb.apps.cluster-kcmwd.kcmwd.sandbox1886.opentlc.com"

client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

#TRANSFORMERS_CACHE = os.environ['TRANSFORMERS_CACHE']
#bootstrap_servers = os.environ['bootstrap_servers']
#topic = os.environ['topic']
#produce_topic = os.environ['produce_topic']
#username = os.environ['username']
#password = os.environ['password']
#sasl_mechanism = os.environ['sasl_mechanism']
#security_protocol = os.environ['security_protocol']

#def analyze_sentiment(text):
#    classifier = pipeline("sentiment-analysis")
#    result = classifier(text)[0]
#    return result["label"]


#bootstrap_servers = ['af421721f4e394a0f85fcab354ff51f0-468260975.us-east-2.elb.amazonaws.com:9092']
topic = 'reviews.moderated'
produce_topic = 'reviews.moderated'
bootstrap_servers = ['kafka-kafka-brokers.globex-mw-user1.svc.cluster.local:9092']
username = 'globex'
password = 'globex'
sasl_mechanism = 'SCRAM-SHA-512'
security_protocol = 'SASL_PLAINTEXT'

#consumer = KafkaConsumer(
#    produce_topic,
#    bootstrap_servers=bootstrap_servers,
#    auto_offset_reset='earliest',
#    enable_auto_commit=True,
#    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
#)

# Set up a Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    sasl_plain_username=username,
    sasl_plain_password=password,
    security_protocol=security_protocol,
    sasl_mechanism=sasl_mechanism,
    auto_offset_reset='latest',
    enable_auto_commit=True,
#    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

#producer = KafkaProducer(
#    bootstrap_servers=bootstrap_servers,
#    value_serializer=lambda m: json.dumps(m).encode('utf-8')
#)

#influxdb_host = 'localhost'
#influxdb_port = 8086
#influxdb_dbname = 'globex'
influxdb_measurement = 'sentiment-measurement'
#influxdb_username = 'globex'
#influxdb_password = 'globex-password'
#influxdb_client = InfluxDBClient(influxdb_host, influxdb_port, influxdb_username, influxdb_password)
#influxdb_client.switch_database(influxdb_dbname)

# Set up a Kafka producer
#producer = KafkaProducer(
#    bootstrap_servers=bootstrap_servers,
#    sasl_plain_username=username,
#    sasl_plain_password=password,
#    security_protocol=security_protocol,
#    sasl_mechanism=sasl_mechanism,
#    value_serializer=lambda m: json.dumps(m).encode('utf-8')
#)

print("Test")
# Start consuming Kafka messages
for message in consumer:
    try:
        # Get the text message from the Kafka message
        #print(message)
        json_payload = message.value
        # Parse the CloudEvent from the JSON payload
        json_data = json.loads(json_payload)
        '''
        json_body = [
            {
                "measurement": influxdb_measurement,
                "time": json_data['time'],
                "fields": {
                    "rating": json_data['data']['rating'],
                    "timestamp": json_data['data']['timestamp'],
                    "score": json_data['data']['score']
                },
                "tags": {
                    "product_id": json_data['data']['product']['product_id'],
                    "product_name": json_data['data']['product']['product_name'],
                    "category": json_data['data']['product']['category'],
                    "name": json_data['data']['user']['name'],
                    "customer_id": json_data['data']['user']['customer_id'],
                    "browser": json_data['data']['user']['browser'],
                    "region": json_data['data']['user']['region'],
                    "response": json_data['data']['response']
                }
            }
        ]'''
        #print(json_data)
        #json_data_data = json_data["data"]
        #print("DATA SPECIFIC INFORMATION")
        #print(json_data_data)
        #point = influxdb_client.Point(json_data_data)
        #print("POINT DATA with JSON ONLY DATA")
        #print(point)
        #point = Point("{bucket}")
        #print(point)
        #point.tag("data", json_data_data["data"])
        #print("POINT TAG")
        #print(point.tag)
        #point.time(parser.parse(json_data["time"]))
        #print(json_data)

        # Create a new InfluxDB data point
        point = influxdb_client.Point(bucket)
        
        #datetime_data = int(json_data_data["timestamp"])
        #print(datetime_data)

        # Set the time for the data point
        timestamp = json_data["timestamp"]
        #print(timestamp)
        if isinstance(timestamp, str):
            timestamp = float(timestamp)

        datetime = datetime.fromtimestamp(timestamp/1000.0)
        #print(datetime)
        #datetime = datetime.strptime(datetime, '%m/%d/%Y, %H:%M:%S')
        datetime_str = datetime.strftime("%m/%d/%Y, %H:%M:%S")
        #print(datetime_str)

        point.time(parser.parse(datetime_str))

        # Flatten the "product" field
        product = json_data["product"]
        #print("Print product information before for loop to flatten it")
        #print(product)

        # Set the "product" fields
        for key, value in json_data["product"].items():
            if key != "product":
                if isinstance(value, dict):
                    # Handle other nested fields if needed
                    pass
                else:
                    point.field(key, value)

            with InfluxDBClient(url, token) as client:
                with client.write_api(write_options=SYNCHRONOUS) as writer:
                    try:
                        writer.write(bucket, org="globex", record=[point])
                    except InfluxDBError as e:
                        print(e)

        # Flatten the "user" field
        user = json_data["user"]
        #print("User data")
        #print(user)

        # Set the remaining fields and tags
        for key, value in json_data["user"].items():
            if key != "user":
                if isinstance(value, dict):
                    # Handle other nested fields if needed
                    pass
                else:
                    point.field(key, value)
                    #print(key,value)

        with InfluxDBClient(url, token) as client:
            with client.write_api(write_options=SYNCHRONOUS) as writer:
                try:
                    writer.write(bucket, org="globex", record=[point])
                except InfluxDBError as e:
                    print(e)

        # Set the remaining fields and tags
        for key, value in json_data.items():
            if key != "user" or key != "data":
                if isinstance(value, dict):
                    # Handle other nested fields if needed
                    pass
                else:
                    point.field(key, value)

        with InfluxDBClient(url, token) as client:
            with client.write_api(write_options=SYNCHRONOUS) as writer:
                try:
                    writer.write(bucket, org="globex", record=[point])
                except InfluxDBError as e:
                    print(e)

    except json.JSONDecodeError:
        print("Non-JSON message received, skipping...")
    except KeyError:
        print("Missing fields in JSON message, skipping...")

