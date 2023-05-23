from pyspark.sql import SparkSession
from pyspark.sql.functions import col,date_format, sum, avg

def init_spark():
  sql = SparkSession.builder\
    .appName("trip-app")\
    .config("spark.jars", "/opt/spark-apps/postgresql-42.2.22.jar")\
    .getOrCreate()
  sc = sql.sparkContext
  return sql,sc

def main():
  url = "jdbc:postgresql://demo-database:5432/mta_data"
  properties = {
    "user": "postgres",
    "password": "casa1234",
    "driver": "org.postgresql.Driver"
  }
  file = "/opt/spark-data/MTA-Bus-Time.txt"
  sql,sc = init_spark()

  df = sql.read.load(file,format = "csv", inferSchema="true", sep="\t", header="true"
      ) \
      .withColumn("report_hour",date_format(col("time_received"),"yyyy-MM-dd HH:00:00")) \
      .withColumn("report_date",date_format(col("time_received"),"yyyy-MM-dd"))
  
  # Filter invalid coordinates
  df.where("latitude <= 90 AND latitude >= -90 AND longitude <= 180 AND longitude >= -180") \
    .where("latitude != 0.000000 OR longitude !=  0.000000 ") \
    .write \
    .jdbc(url=url, table="mta_reports", mode='append', properties=properties)

  # Aggregation 1: Calculate total distance traveled by every vehicle
  total_distance = df.groupBy("vehicle_id").agg(sum("distance_along_trip"))

  # Aggregation 2: Average distance along trip by vehicle
  avg_distance_along_trip = df.groupBy("vehicle_id").agg(avg("distance_along_trip"))

  # Write the aggregations to PostgreSQL
  total_distance.write.jdbc(url=url, table="total_distance_by_vehicle", mode='append', properties=properties)
  avg_distance_along_trip.write.jdbc(url=url, table="average_speed_by_vehicle", mode='append', properties=properties)
  
if __name__ == '__main__':
  main()