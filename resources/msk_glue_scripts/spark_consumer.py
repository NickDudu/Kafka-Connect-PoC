import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkConf
from pyspark.sql.session import SparkSession
from datetime import datetime
import boto3
#from delta import *
#from delta.tables import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BinaryType
from pyspark.sql.functions import *
#import org.apache.avro.SchemaBuilder

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

glue_region = "ap-northeast-1"
glue_schema_registry_name = "legopoc"
glue_schema_name = "fullfillment.test_db.person"
glue_schema_version = "latest"

#Glue boto3 to read schema
session = boto3.Session(aws_access_key_id='xxxx', aws_secret_access_key='xxxx')
glue_client = session.client('glue' , region_name='ap-northeast-1')
response = glue_client.list_registries(
    MaxResults=23
)

schema_message = glue_client.get_schema_version(
    SchemaId={
        'SchemaName': 'fullfillment.test_db.person',
        'RegistryName': 'legopoc'
    },
    SchemaVersionNumber={
        'LatestVersion': True
    }
)


'''A buffer is allocated for the serialized message. A header of 18 bytes is
written. * Byte 0 is an 8 bit version number * Byte 1 is the compression *
Byte 2-17 is a 128 bit UUID representing the schema-version-id/'''

avro_schema = schema_message['SchemaDefinition']

def trim_gsr_avro_udf(raw_record):
    raw_record = raw_record[18:]
    return raw_record
    
spark.udf.register("trim_gsr_avro", trim_gsr_avro_udf)
trim_gsr_avro = udf(trim_gsr_avro_udf, BinaryType())


print(schema_message['SchemaDefinition'])
avro_schema = schema_message['SchemaDefinition']


df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "xxxx:9092") \
    .option("subscribe", "fullfillment.test_db.person") \
    .option("startingOffsets", "earliest") \
    .load()
  
df.printSchema

#df.printSchema
from pyspark.sql.avro.functions import from_avro, to_avro
newdf = df.select(from_avro(trim_gsr_avro(df.value), avro_schema).alias("data")).select("data.*")
newdf.printSchema

parquet_query = newdf \
    .writeStream \
    .format("console") \
    .start()

parquet_query.awaitTermination()

job.commit()