from aiokafka import AIOKafkaConsumer
import asyncio


KAFKA_HOST = 'kafka:9092'
KAFKA_TOPIC = 'common'
KAFKA_GROUP = 'common_group'


async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_HOST,
        group_id=KAFKA_GROUP)
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


if __name__ == '__main__':
    print(f'satrt consuming topic {KAFKA_TOPIC} from host {KAFKA_HOST}')
    asyncio.run(consume())