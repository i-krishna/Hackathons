import psycopg2

# Redshift connection parameters
host = "cluster-name.region.redshift.amazonaws.com"
port = 5439  # default port
user = "username"
password = "password"
dbname = "dbname"

# Connect to Redshift
conn = psycopg2.connect(
    dbname=dbname,
    user=user,
    password=password,
    host=host,
    port=port
)
conn.autocommit = True

# Create a cursor object
cur = conn.cursor()

# SQL to load data from S3 to Redshift
copy_sql = """
COPY your_table
FROM 's3://bucket-name/data-file.csv'
IAM_ROLE 'arn:aws:iam::123456789012:role/RedshiftRole'
FORMAT AS CSV;
"""

# Execute the COPY command
cur.execute(copy_sql)

# Close the cursor and connection
cur.close()
conn.close()
