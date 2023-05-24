# Spark Cluster with Docker and postgreSQL database

# General

A basic spark standalone cluster which analyizes bus stop data from the MTA in NYC and stores the results in a postgreSQL Database. HDFS is not used in this example instead the files are just stored on the local filesystem on every node in the cluster.

# Installation instructions

## Build the image

Execute the following command in the directory where the Dockerfile is located:
```sh
docker build -t cluster-apache-spark:3.0.2 .
```

## Run docker-compose

Execute the following command in the directory where the docker-compose.yml is located:
```sh
docker-compose up -d
```

Following containers will be created:

container|Exposed ports
---|---
spark-master|9090 7077
spark-worker-A|9091
spark-worker-B|9092
demo-database|5432

# Binded Volumes

Two volumes are binded to the containers. The volumes are used to share data between the containers and the host system.

Host Mount|Container Mount|Purposse
---|---|---
apps|/opt/spark-apps| Make your applications available on all workers & master
data|/opt/spark-data| Make your data available on all workers & master



# Run application

## Download data sets and analyze the data

This application just loads archived data from [MTA Bus Time](http://web.mta.info/developers/MTA-Bus-Time-historical-data.html). Renaming of the downloaded file in main.py and mta.conf is needed. 
Filters and aggregations are used to anaylize the data with Spark. The result is persisted into a postgreSQL table.

The following image defines the columns in the data file:
<img src="images/Column_def.jpg" alt="Date Field Definitions" width="600" height="500">

To submit the app connect to one of the workers or master:
```sh
docker exec -it <container-id> bash
```
Submit the app to the spark cluster:

```sh
/opt/spark/bin/spark-submit --master spark://spark-master:7077 \
--jars /opt/spark-apps/postgresql-42.2.22.jar \
--driver-memory 1G \
--executor-memory 1G \
/opt/spark-apps/main.py
```

## Review Data In postgreSQL

Connect to the database container:

```sh
docker exec -it <container-id> psql -U postgres
```

Switch to the database:

```sh
\c mta_data
```

List tables:

```sh
\dt
```

Review the data:

```sh
SELECT * FROM mta_reports;
```



