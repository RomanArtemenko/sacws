import logging
import sys
from logging import StreamHandler, Formatter

import asyncio
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

import asyncio
import aio_pika


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        print(message.body)
        logger.info('got rabbit message: {}'.format(message.body))
        await asyncio.sleep(1)


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
    	# logger.info('got kafka message: {}'.format(msg.value))
        logger.info(f'satrt consuming from host {RABBITMQ_HOST}:{RABBITMQ_PORT}')
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
        logger.info('rabbit consumer stop')   	
