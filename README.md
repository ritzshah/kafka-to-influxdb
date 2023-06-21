# kafka-to-influxdb

 Data to be moved from Kafka Topic and Influxdb.

Following is the data format :
 ```yaml
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
```

You will need to ocnfigure Kafka Consumer and InfluxDB Client.
