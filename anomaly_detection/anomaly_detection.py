'''
Consumer that receives EV data and detects anomaly and
Passes the detection result to monitoring through MQ
'''

from typing import Set, Any, final
from venv import create
from kafka import TopicPartition
import pandas as pd

import asyncio
import json
import os
from joblib import load
from multiprocessing import Process

import numpy as np
import pika
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from utils.utils import create_consumer, get_logger

# Pick either Isolation Forest or Extended Isolation Forest
# model_path = os.path.abspath('./anomaly_detection/isolation_forest.joblib')
model_path = os.path.abspath('./anomaly_detection/extended_isolation_forest.joblib')

# Get the logger
logger = get_logger()

# global variables
consumer_task = None
consumer = None
_data = 0

# Initialize function that creates consumer and async task to consume
async def initialize():
    loop = asyncio.get_event_loop()
    global consumer

    consumer = create_consumer(loop)

    await consumer.start()

    c_task = loop.create_task(receive_message(consumer))
    await c_task
    try:
        loop.run_forever()
    finally:
        await consumer.stop()
        c_task.cancel()
        loop.stop()
        loop.close()

# Receive the message and perform detection         
async def receive_message(consumer):
    while True:
        try:
            # consume messages
            async for msg in consumer:
                # update the API state
                await _detect_anomaly(msg)
        except Exception as e:
            logger.warning(f'Error {e}')

        finally:
            # will leave consumer group; perform autocommit if enabled
            logger.warning(f'Stopping ')
            await consumer.stop()

# Send the detection result to MQ consumer
def _send_rbmq_message(message):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='ev-station-anomaly')

    channel.basic_publish(exchange='', routing_key='ev-station-anomaly', body=message)
    print(f" [x] Sent {message}")
    connection.close()

# Detects the anomaly using the model and sends the result
async def _detect_anomaly(message: Any) -> None:
    record = json.loads(json.loads(message.value))
    global _state
    _data = pd.DataFrame(record, index=[0])

    result = anomaly_detection_model.predict(_data.to_numpy())

    if type(result) == bool:
        record["anomaly"] = result
    else:
        record["anomaly"] = True if result else False

    record = json.dumps(record).encode("utf-8")

    # Add Rabbitmq message
    _send_rbmq_message(record)

# Start the Anomaly detection async
async def start_anomaly_detection():
    global anomaly_detection_model
    logger.info('Initializing API ...')
    await initialize()

if __name__== "__main__":
    # Loading the model
    anomaly_detection_model = load(model_path)
    asyncio.run(start_anomaly_detection())
