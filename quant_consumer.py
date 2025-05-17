from pyspark.sql.types import StructType, DoubleType, StructField, LongType
from pyspark.sql import SparkSession
import pyspark.sql.functions as F

spark = SparkSession.builder.appName("StreamQuant").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

schema = StructType([
  StructField('timestamp', LongType()),
  StructField('open', DoubleType()),
  StructField('high', DoubleType()),
  StructField('low', DoubleType()),
  StructField('close', DoubleType()),
  StructField('volume', DoubleType())
])

df_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "StreamQuant") \
    .option("startingOffsets", "latest") \
    .load()

df_raw = df_raw.selectExpr("CAST(value AS STRING)")

df_raw = df_raw.withColumn("value", F.from_json(df_raw.value, schema))\
    .select("value.*")  

df_raw = df_raw.withColumn("datetime", F.from_unixtime(F.col("timestamp") / 1000))

df_raw.writeStream \
 .format("parquet") \
 .option("path", "/tmp/stream_output/") \
 .option("checkpointLocation", "/tmp/stream_checkpoint/") \
 .outputMode("append") \
 .start() \
 .awaitTermination()