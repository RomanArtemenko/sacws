import logging
import sys
from logging import StreamHandler, Formatter

import asyncio
from aiokafka import AIOKafkaConsumer
from aio_pika import connect, Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = StreamHandler(stream=sys.stdout)
handler.setFormatter(Formatter(fmt='[%(asctime)s: %(levelname)s] %(filename)s %(lineno)d: %(message)s'))
logger.addHandler(handler)


# kafka
KAFKA_HOST = 'kafka:9092'
KAFKA_TOPIC = 'common'
KAFKA_GROUP = 'common_group'

# rabbitMQ
RABBITMQ_USER = 'admin'
RABBITMQ_PASS = 'admin'
RABBITMQ_VHOST = '/'
RABBITMQ_HOST = 'rabbit'
RABBITMQ_PORT = 5672


async def publisher(msg, loop):
    # Perform connection
    connection = await connect(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASS,
        virtualhost=RABBITMQ_VHOST,
        loop=loop
    )

    # Creating a channel
    channel = await connection.channel()

    # set queue
    await channel.declare_queue('hello', auto_delete=True)

    # Sending the message
    await channel.default_exchange.publish(
        Message(msg),
        routing_key="hello",
    )

    logger.info('Sent message: {}'.format(msg))

    await connection.close()


async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_HOST,
        group_id=KAFKA_GROUP)
    # Get cluster layout and join group `my-group`
    await consumer.start()
    logger.info('Start kafka consumer')
    try:
        # Consume messages
        async for msg in consumer:
            logger.info('got kafka message: {}'.format(msg.value))
            try:
                await publisher(msg.value, asyncio.get_running_loop())
            except Exception as e:
                logger.error("Error: {}".format(e))
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        logger.info('kafka consumer stop')
        await consumer.stop()


if __name__ == '__main__':
    logger.info(f'satrt consuming topic {KAFKA_TOPIC} from host {KAFKA_HOST}')
    asyncio.run(consume())
