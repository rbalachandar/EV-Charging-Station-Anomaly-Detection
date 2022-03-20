'''
Kafka Producer of EV Station Data
'''

import json
import random
import time
from datetime import datetime
import numpy as np
import pandas as pd
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from config import EV_STATION_TOPIC, DELAY, OUTLIERS_THRESHOLD_PROBABILITY
from utils.utils import create_producer, load_ev_data

_id = 0
# Create Kafka Producer
producer = create_producer()

# Loading EV Charging data and performing data filtering and transformation
ev_data = None
ev_data_frame = None

# Load the EV data
ev_data_frame = load_ev_data()

""" Send EV Data to consumer """
if producer is not None:
    while True:
        for index, data in ev_data_frame.iterrows():
        # Generate EV observations
            record = data.to_json()
            #print(record)
            record = json.dumps(record).encode("utf-8")

            producer.produce(topic=EV_STATION_TOPIC,
                            value=record,
                            key=str(_id))
            producer.flush()
            _id += 1
        time.sleep(DELAY)