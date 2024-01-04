from hdfs_functions import file_permission, delete_file, rename_file, delete_dir, dir_permission
from hdfs_functions import ingest as hdfs_ingest
from job_monitoring_functions import getProcessID, startJobExecution, initialize_PID, setStatus, getJobStatus, startJobStepExecution, setStatusJobStepExecution, getProcessStepID
import datetime
from pyspark.sql import SparkSession, SQLContext, HiveContext
from pyspark.sql.functions import *
from pyspark.sql import functions as F
import sys
import findspark
import os
from pyspark.sql.functions import current_date, col
from pyspark.sql import Row 
from hash_gen import md5_hash
from add_columns_to_csv import lower_col_names, add_column
from pyspark.sql.types import *
from typing import List
import re
import json

#1. GLOBAL VALUES
def ingest(spark, key_obj, pid):

	hdfs_ingest(key_obj['local_loc'], key_obj['hdfs_loc'])
	file_permission(key_obj['hdfs_file_loc'])

def load_rawvault(spark, key_obj, pid):

#2. LOAD RAWVAULT - adds columns process_id and insert_tst to original csv

	rawvault = spark.sql("select * from {0}.{1}".format(key_obj['source_database'], key_obj['table_name'].lower()))
	json_rawvault_schema = rawvault.schema.json()

	structType_rawvault_schema = StructType.fromJson(json.loads(json_rawvault_schema))
	bad_record_column = [StructField("bad_record", StringType(), True)]
	customschema = StructType(structType_rawvault_schema.fields + bad_record_column)
	
	local_df = (spark.read.format("com.databricks.spark.csv")
		.option("badRecordsPath", "/shared/HIVE-Table-Data/bad_records/")
		.option("columnNameOfCorruptRecord", "bad_record")
		.options(header="true")
		.csv(key_obj['hdfs_file_loc'], header=True, schema=customschema)
	)

	#local_df.printSchema()

	# lower column names in local_df:
	local_df = lower_col_names(local_df)

	#local_df.show()

	# Works with the assumption we know atleast one non-nullable column in our dataset.
	local = local_df.filter("id is NULL")

	local.show()

	# write the complete bad_rows spark dataframe to hdfs location below 
	#loc_to_store = '/shared/bad_records' + hdfs_file_loc.split('/')[-1]
	loc_to_store = 'hdfs://localhost/tmp/ingest/bad_records/'+ key_obj['hdfs_file_loc'].split('/')[-1]

	print(loc_to_store)

	local\
		.coalesce(1)\
		.write\
		.format('com.databricks.spark.csv')\
		.mode("overwrite")\
		.options(header='true')\
		.save(loc_to_store)

	#change the permission to above dir loacation for any user to rwx
	dir_permission(loc_to_store)

	df = (spark.read.format("csv")
		.csv(key_obj['hdfs_file_loc'], header=True, schema=structType_rawvault_schema)
		)

	local_df = df.na.drop(how="all")

	rawvault_df = (local_df.withColumn('process_id', lit(pid))
			.withColumn('insert_tst', lit(F.current_timestamp()))
			.withColumn('tenant_name', lit(key_obj['tenant_name']))
			.withColumn('source_system', lit(key_obj['source_system'])))
	#rawvault_df.show()

	cols = []
	#partitions = ["process_id", "tenant_name"]
	for col in rawvault_df.columns:
		if col not in key_obj['partitions']:
			cols.append(col)
	cols.extend(key_obj['partitions'])

	rawvault_df = rawvault_df.select(cols)

	rawvault_df.registerTempTable("temptable")
	
	spark.sql("insert into table {0}.{1} select * from temptable".format(key_obj['source_database'], key_obj['table_name'].lower()))
	
	return (rawvault_df)

def load_core(spark, key_obj, pid, source):

#3. LOAD CORE - Adds more columns and does hasing

	## select columns to hash 

	id_columns = source.select(*sorted(key_obj['primaryKeys']['id']['fields']))

	sid_columns = source.select(*sorted(key_obj['primaryKeys']['sid']['fields']))
	columns_to_drop_for_diff_hash = ['process_id', 'insert_tst']  
	df = source.drop(*columns_to_drop_for_diff_hash)

	id_key = md5_hash(id_columns.columns)	
	sid = md5_hash(sid_columns.columns)
	diff_hash = md5_hash(df.columns)
	
	source = (source.withColumn(key_obj['primaryKeys']['id']['field_name'], id_key)
                       .withColumn(key_obj['primaryKeys']['sid']['field_name'],sid)
                       .withColumn("diff_hash", diff_hash)
		)

	columns_to_drop_for_record_hash = ['process_id', 'insert_tst', key_obj['primaryKeys']['sid']['field_name']]

	df_record_hash = source.drop(*columns_to_drop_for_record_hash)

	record_hash = md5_hash(df_record_hash.columns)

	source = source.withColumn("record_hash", record_hash)    

	cols = []
	#partitions = ["process_id", "tenant_name"]
	for col in source.columns:
		if col not in key_obj['partitions']:
			cols.append(col)
	cols.extend(key_obj['partitions'])

	source = source.select(cols)
	
	core_df = spark.sql("select * from {0}.{1}".format(key_obj['target_database'],key_obj['table_name']))

	join_condition = [source["diff_hash"] == core_df["diff_hash"], source["tenant_name"] == core_df["tenant_name"], source[key_obj["primaryKeys"]["id"]["field_name"]] == core_df[key_obj["primaryKeys"]["id"]["field_name"]]]

	print("before join:",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	join_result = source.join(core_df, join_condition,'left_anti')
	print("after join:",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	
	join_result.show()
	join_result.registerTempTable("temp")
	
	print("rows in "+ key_obj['source_database']+" of table "+key_obj['table_name'], spark.sql("select * from {0}.{1}".format(key_obj['source_database'],key_obj['table_name'].lower())).count())
	print("rows in "+ key_obj['target_database']+" of table "+key_obj['table_name'], spark.sql("select * from {0}.{1}".format(key_obj['target_database'],key_obj['table_name'].lower())).count())
	print("rows in temptable to be inserted from: ", spark.sql("select * from temp").count())

	print("before "+key_obj['table_name']+" insert:",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	spark.sql("insert into {0}.{1}  select * from temp".format(key_obj['target_database'],key_obj['table_name'].lower(),pid,key_obj['tenant_name'])) 
	
	print("after "+key_obj['table_name']+" insert:",datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
	
#4. writing spark df to hive directly

#source1.write.mode("append").insertInto("core.lv_test7")
