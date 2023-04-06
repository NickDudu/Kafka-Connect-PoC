from aws_schema_registry import SchemaRegistryClient, DataAndSchema, SchemaRegistryClient
from aws_schema_registry.avro import AvroSchema
from aws_schema_registry.adapter.kafka import KafkaDeserializer
from kafka import KafkaConsumer
import boto3
from time import sleep
from json import dumps

session = boto3.Session(aws_access_key_id='xxxx', aws_secret_access_key='xxxx')
glue_client = session.client('glue' , region_name='ap-northeast-1')

# Create the schema registry client, which is a façade around the boto3 glue client
client = SchemaRegistryClient(glue_client, registry_name='xxxx')
                              
# Create the deserializer
deserializer = KafkaDeserializer(client)


consumer = KafkaConsumer('fullfillment.test_db.Person',
                         value_deserializer=deserializer,
                         auto_offset_reset='earliest',
                         bootstrap_servers=['xxxx:9092'])
                         
for message in consumer:
    # The deserializer produces DataAndSchema instances
    value: DataAndSchema = message.value
    # which are NamedTuples with a `data` and `schema` property
    value.data == value[0]
    value.schema == value[1]
    # and can be deconstructed
    data, schema = value
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          data))