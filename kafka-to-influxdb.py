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
from cloudevents.http import CloudEvent
from cloudevents.http import from_http
from cloudevents.conversion import to_binary
import requests

'''
requirements.txt
kafka-python
transformers
torch
pytorch
influxdb
influxdb-client
'''

#Define all Variables
TRANSFORMERS_CACHE = os.environ['TRANSFORMERS_CACHE']
bootstrap_servers = os.environ['bootstrap_servers']
username = os.environ['username']
password = os.environ['password']
sasl_mechanism = os.environ['sasl_mechanism']
security_protocol = os.environ['security_protocol']
topic = os.environ['topic']
reviews_sentiment_sink = os.environ['reviews_sentiment_sink']
attributes = {
    "type": os.environ['ce_type'],
    "source": os.environ['ce_source']
}

bucket = os.environ['bucket']
org = os.environ['org']
token = os.environ['influxdb-token']
# Store the URL of your InfluxDB instance
url = os.environ['influxdb-url']
influxdb_measurement = os.environ['influxdb-measurement']

# Setup influxdb client and Kafka Topic
client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

print(client)

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

# Start consuming Kafka messages
for message in consumer:
    try:
        # Get the text message from the Kafka message
        #print(message)
        json_payload = message.value
        # Parse the CloudEvent from the JSON payload
        json_data = json.loads(json_payload)
        prin("Printing consumer message")
        print(json_data)
        # Create a new InfluxDB data point
        point = influxdb_client.Point(bucket)

        # Set the time for the data point
        timestamp = json_data["timestamp"]
        #print(timestamp)
        if isinstance(timestamp, str):
            timestamp = float(timestamp)

        datetime = datetime.fromtimestamp(timestamp/1000.0)
        datetime_str = datetime.strftime("%m/%d/%Y, %H:%M:%S")

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
                    print("In product")
                    print(key,value)

            with InfluxDBClient(url, token) as client:
                with client.write_api(write_options=SYNCHRONOUS) as writer:
                    try:
                        writer.write(bucket, org, record=[point])
                    except InfluxDBError as e:
                        print(e)

        # Flatten the "user" field
        user = json_data["user"]

        # Set the remaining fields and tags
        for key, value in json_data["user"].items():
            if key != "user":
                if isinstance(value, dict):
                    # Handle other nested fields if needed
                    pass
                else:
                    point.field(key, value)

        with InfluxDBClient(url, token) as client:
            with client.write_api(write_options=SYNCHRONOUS) as writer:
                try:
                    writer.write(bucket, org, record=[point])
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
                    writer.write(bucket, org, record=[point])
                except InfluxDBError as e:
                    print(e)

    except json.JSONDecodeError:
        print("Non-JSON message received, skipping...")
    except KeyError:
        print("Missing fields in JSON message, skipping...")

