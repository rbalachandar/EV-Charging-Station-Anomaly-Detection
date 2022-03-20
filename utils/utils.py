'''
Utilities
'''

import logging
import socket
import pandas as pd
import json
from random import randint
from confluent_kafka import Producer, Consumer
import aiokafka
from config import KAFKA_BROKER, EV_STATION_TOPIC

# env variables
KAFKA_CONSUMER_GROUP_PREFIX = 'ev-station-data'
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'


def get_logger():
    """Get Logger

    Returns:
        logger: logger instance
    """
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    logger = logging.getLogger(__name__)

    return logger   

# Logger Instance
logger = get_logger()

def create_producer() -> Producer:
    """Creates Kafka Producer

    Returns:
        Producer: Instance of Kafka Producer
    """
    try:
        producer = Producer({"bootstrap.servers": KAFKA_BROKER,
                             "client.id": socket.gethostname(),
                             "enable.idempotence": True,  # EOS processing
                             "compression.type": "lz4",
                             "batch.size": 64000,
                             "linger.ms": 10,
                             "acks": "all",  # Wait for the leader and all ISR to send response back
                             "retries": 5,
                             "delivery.timeout.ms": 1000})  # Total time to make retries
    except Exception as e:
        logging.exception("Couldn't create the producer")
        producer = None

    return producer


def create_consumer(loop) -> Consumer:
    """Create Kafka Consumer

    Args:
        loop (event loop): Event loop for Kafka consumer

    Returns:
        Consumer: Instance of Kafka consumer
    """
    try:
        group_id = f'{KAFKA_CONSUMER_GROUP_PREFIX}-{randint(0, 10000)}'
        logger.debug(f'Initializing KafkaConsumer for topic {EV_STATION_TOPIC}, group_id {group_id}'
                f' and using bootstrap servers {KAFKA_BOOTSTRAP_SERVERS}')
        consumer = aiokafka.AIOKafkaConsumer(EV_STATION_TOPIC, loop=loop,
                                            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                                            group_id=group_id)
    except Exception as e:
        logging.exception("Couldn't create the consumer")
        consumer = None
    
    return consumer

def load_ev_data():
    """Loads EV data from data file and converts into Dataframe

    Returns:
        DataFrame: EV Data filtered 
    """
    ev_data_frame = None

    with open("./data/acndata_sessions.json") as json_file:
        ev_data = json.loads(json_file.read())
        ev_data_frame = pd.DataFrame.from_dict(ev_data["_items"], orient="columns")
        print(ev_data_frame.info())   

        ev_data_frame.dropna(inplace=True)
        ev_data_frame.drop(columns=["_id", "clusterID", "userID", "spaceID", "timezone", "siteID"], inplace=True)

        ev_data_frame["userInputs"] = ev_data_frame["userInputs"].str[0]
        ev_data_frame = pd.concat([ev_data_frame.drop(["userInputs"], axis=1), ev_data_frame["userInputs"].apply(pd.Series)], axis=1)    
        ev_data_frame.drop(columns=["WhPerMile", "milesRequested", "minutesAvailable", "modifiedAt", "paymentRequired", "requestedDeparture", "sessionID", "stationID"], inplace=True)
        ev_data_frame[["connectionTime", "disconnectTime", "doneChargingTime"]] = ev_data_frame[["connectionTime", "disconnectTime", "doneChargingTime"]].apply(pd.to_datetime)
        # ev_data_frame["connectionDuration"] = (ev_data_frame.disconnectTime-ev_data_frame.connectionTime).astype('timedelta64[h]')
        ev_data_frame["chargingDuration"] = (ev_data_frame.doneChargingTime-ev_data_frame.connectionTime).astype('timedelta64[h]')
        ev_data_frame.drop(columns=["connectionTime", "disconnectTime", "doneChargingTime", "userID"], inplace=True)

    return  ev_data_frame