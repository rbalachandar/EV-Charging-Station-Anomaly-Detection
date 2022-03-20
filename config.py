import os
from os.path import join, dirname

DELAY = 0.01
OUTLIERS_THRESHOLD_PROBABILITY = 0.2
KAFKA_BROKER = "localhost:9092"
EV_STATION_TOPIC = "ev-station-data"
EV_STATION_CONSUMER_GROUP = "ev-station-data"
NUM_PARTITIONS = 3
