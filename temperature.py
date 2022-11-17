import boto3
import json
from random import uniform
import time
from datetime import datetime

aws_access_key_id = '<your_aws_access_key_id>'
aws_secret_access_key = '<your_aws_secret_access_key>'
region_name = '<your_region_name>'
kinesis_stream_name = 'wind_farm_project'

kinesis_client = boto3.client(
    'kinesis',
    aws_access_key_id = aws_access_key_id,
    aws_secret_access_key = aws_secret_access_key,
    region_name = region_name
)

id = 0
while True:
  
  data = uniform(20, 25)
  id += 1

  register = {'id': str(id), 'data': str(data), 'type': 'temperature', 'timestamp': str(datetime.now())}

  kinesis_client.put_record(
      StreamName = kinesis_stream_name,
      Data = json.dumps(register),
      PartitionKey='02'
      )
  
  time.sleep(10)