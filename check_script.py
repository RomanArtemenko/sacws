from aiokafka import AIOKafkaProducer
import asyncio
import json
import uuid


KAFKA_HOST = 'kafka:9092'
KAFKA_TOPIC = 'common'


save_geometry = {
    "sender": "checker",
    "action": "save_geometry",
    "key": "5e02a64d-d52b-4e75-bcd6-dfbe83735e14",
    "params":{
    	"type": "Feature",
    	"properties": {},
    	"geometry": {
    		"type": "Polygon",
    		"coordinates": [
    			[
    				[-101.949692, 39.422403],
    				[-102.036896, 39.351821],
    				[-101.978531, 39.260436],
    				[-101.848068, 39.247676],
    				[-101.770477, 39.310394],
    				[-101.757431, 39.388979],
    				[-101.852188, 39.434602],
    				[-101.949692, 39.422403]
    			]
    		]
    	}
    }
}



async def produce_event(loop):
    producer = AIOKafkaProducer(loop=loop, bootstrap_servers=KAFKA_HOST)
    await producer.start()
    try:
        await producer.send_and_wait(
            KAFKA_TOPIC, json.dumps(save_geometry).encode('utf-8'))
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()
    print(f'Msg was send to topic {KAFKA_TOPIC} !')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(produce_event(loop))
