import json
import hashlib
import logging
import sys
from logging import StreamHandler, Formatter

import asyncio
import asyncpg
import aio_pika
from aio_pika import connect, Message


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(filename)s %(lineno)d: %(message)s'))
logger.addHandler(handler)


# rabbitMQ
RABBITMQ_USER = 'admin'
RABBITMQ_PASS = 'admin'
RABBITMQ_VHOST = '/'
RABBITMQ_HOST = 'rabbit'
RABBITMQ_PORT = 5672

# postgres
POSTGRES_USER = 'geo'
POSTGRES_PASSWORD = 'geo'
POSTGRES_DB = 'geo'
POSTGRES_HOST = 'postgres'


async def save_to_db(shape_hash, shape):
	conn = await asyncpg.connect(user=POSTGRES_USER, password=POSTGRES_PASSWORD,
                                 database=POSTGRES_DB, host=POSTGRES_HOST)

	res = await conn.fetch('''
		INSERT INTO geo_data(hash, shape) 
		VALUES($1, ST_GeomFromGeoJSON($2))''',
		shape_hash, shape)

	await conn.close()


async def process_message(msg: aio_pika.IncomingMessage):
    async with msg.process():
        logger.info('got rabbit message: {}'.format(msg.body))
        msg_json = json.loads(msg.body)
        params = msg_json['params']
        geometry_hash = hashlib.md5(repr(params['geometry']).encode()).hexdigest()
        logger.info('msg_json: {}'.format(msg_json))
        logger.info('geometry_hash: {}'.format(geometry_hash))
        await save_to_db(geometry_hash, json.dumps(params['geometry']))


async def main(loop):
    connection = await aio_pika.connect_robust(
    	host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASS,
        virtualhost=RABBITMQ_VHOST, 
        loop=loop
    )

    queue_name = "hello"

    # Creating channel
    channel = await connection.channel()

    # Maximum message count which will be
    # processing at the same time.
    await channel.set_qos(prefetch_count=100)

    # Declaring queue
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    await queue.consume(process_message)

    return connection


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main(loop))

    try:
        logger.info(f'satrt consuming from host {RABBITMQ_HOST}:{RABBITMQ_PORT}')
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
        logger.info('rabbit consumer stop')   	
