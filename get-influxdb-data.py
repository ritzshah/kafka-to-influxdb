# Define the query to retrieve the data
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

query = 'from(bucket: "globex-bucket") |> range(start: 0) |> filter(fn: (r) => r._measurement == "globex-bucket")'

# Run the query
query_api = client.query_api()
result = query_api.query(query)

# Check if any data points are returned
if result:
    # Iterate over the result and print the data points
    for table in result:
        for record in table.records:
            print(record.values)
else:
    print("No data points found in InfluxDB.")
