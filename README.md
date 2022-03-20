# EV-Charging-Station-Anomaly-Detection

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Architecture](#architecture)
* [Services](#services)
* [Data Engineering](#data-engineering)
* [Anomaly Model Training](#anomaly-model-training)
* [Setup](#setup)
* [Run](#run)

## General info
Detecting anomalies in EV charging station is key to prevent loss of energy. In this project the EV usage anomaly is detected using Kafka streaming and RabbitMq services and Isolation Forest unsupervised learning method. The EV Charing Station KPIs (User, Meter Usage, Temperature, etc) are simulated using Kafka producer that produces real-time data stream from Adaptive Charging Network (ACN-Data) https://ev.caltech.edu/dataset. 
Anomaly detection engine consumes the data and gives the anomaly score which is monitored through RabbitMQ Pub-Sub mechanism. 
The detected anomaly can be alerted using email and dashboard notifications.
	
## Technologies
Project is developed with:
* Python, Pandas, Apache Kafka, RabbitMQ, AsyncIO
* Scikit-Learn Isolation Forest

## Architecture

![EV Charging Anomaly Detection](https://user-images.githubusercontent.com/16436690/151078560-3aee3e0c-7772-4743-a818-f996b5c985a6.png)


## Services
* Kafka Streaming 
* Anomaly Detection Engine
* Monitoring Service
* Alerting Service
* Dashboard Service

## Data Engineering
The EV charging station dataset (https://ev.caltech.edu/dataset) has following information
Data columns (total 13 columns):
| # |  Column  |  Non-Null Count | Dtype |
| --- |  --- |  --- |  --- | 
| 0  | _id               | 16117 non-null | object 
| 1  | clusterID         | 16117 non-null | object 
| 2  | connectionTime    | 16117 non-null | object 
| 3  | disconnectTime    | 16117 non-null | object 
| 4  | doneChargingTime  | 14070 non-null | object 
| 5  | kWhDelivered      | 16117 non-null | float64
| 6  | sessionID         | 16117 non-null | object 
| 7  | siteID            | 16117 non-null | object 
| 8  | spaceID           | 16117 non-null | object 
| 9  | stationID         | 16117 non-null | object 
| 10 | timezone          | 16117 non-null | object 
| 11 | userID            | 13888 non-null | object 
| 12 | userInputs        | 13888 non-null | object 

For Anomaly detection, connection duration, charging time, kWhRequested and kWhDelivered are used.
Connection duration is calculated from connection time and disconnection time 
Charging duration is calculated from connection time and doneCharging time
Null/NA are dropped
| # |  Column  |  Non-Null Count | Dtype |
| --- |  --- |  --- |  --- | 
| 0 |  kWhDelivered       | 11997 non-null | float64
| 1 |  kWhRequested       | 11997 non-null | float64
| 2 |  chargingDuration   | 11997 non-null | float64

## Data Engineering
Model parameters are tuned using GridSearchCV
Both Isolation Forest and Extended Isolation Forest are trained and predicted. 
Model is analyzed using SHAP values
Python Notebook available in anomaly_detection folder
## Setup

```
Download and Extract Kafka
Download and install RabbitMQ
$ brew install librdkafka
$ C_INCLUDE_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/include LIBRARY_PATH=/opt/homebrew/Cellar/librdkafka/1.8.2/lib pip install confluent_kafka
Create topic 'ev-station-data' for the producer (EV-station) will send new records using:
$ bin/kafka-topics.sh --bootstrap-server localhost:9092 --topic ev-station-data --create --partitions 3 --replication-factor 1
$ pip install pika
Installing Shap on Mac
To overcome llvm-config not found errors:
$ brew install llvm@11
$ LLVM_CONFIG=/opt/homebrew/opt/llvm@11/bin/llvm-config pip install llvmlite
$ pip install shap
```

## Run

```
Start Kafka Zookeeper
$ bin/zookeeper-server-start.sh config/zookeeper.properties
Start Kafka Server
$ bin/kafka-server-start.sh config/server.properties
Start RabbitMq Server
$ rabbitmq-server
Start EV Station Data Producer
$ python producer/ev_station.py
Start Anomaly Detector
$ python anomaly-detection/anomaly_detection.py
```
