import json
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Read configuration file from S3
config_path = "s3://path-to-your-config-file/config.json"
config_content = spark.read.text(config_path).collect()[0][0]
config = json.loads(config_content)

JOB_NAME = config.get('JOB_NAME', 'default_job_name')
DATABASE = config.get('DATABASE', 'default_database')
TABLE_NAME = config.get('TABLE_NAME', 'default_table')
S3_PATH = config.get('S3_PATH', 's3://your-bucket/your-path/')

job = Job(glueContext)
job.init(JOB_NAME, {})

datasource0 = glueContext.create_dynamic_frame.from_catalog(database=DATABASE, table_name=TABLE_NAME, transformation_ctx="datasource0")

# Data transformations (also via workflows in IICS GUI)
transformed_datasource = ApplyMapping.apply(frame=datasource0, mappings=[("col1", "string", "col1", "string"), ("col2", "int", "col2", "int")])

# Write out the data to S3
datasink4 = glueContext.write_dynamic_frame.from_options(frame=transformed_datasource, connection_type="s3", connection_options={"path": S3_PATH}, format="parquet", transformation_ctx="datasink4")

job.commit()
