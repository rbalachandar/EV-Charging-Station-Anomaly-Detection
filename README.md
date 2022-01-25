# EV-Charing-Station-Anomaly-Detection

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Architecture](#architecture)
* [Services](#services)
* [Setup](#setup)

## General info
Detecting anomalies in EV charging station is key to prevent loss of energy. In this project the EV usage anomaly is detected using Kafka services and Isolation Forest unsupervised learning method. The EV Charing Station KPIs (User, Meter Usage, Temperature, etc) are simulated using Kafka producer that produces real-time data stream. Anomaly detection engine consumes the data and gives the anomaly score which is monitored through RabbitMQ Pub-Sub mechanism. The detected anomaly can be alerted using email and dashboard notifications.
	
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

## Setup
TODO:

```
$ cd ../lorem
$ npm install
$ npm start
```


