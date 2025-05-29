import json

from public.channel import get_connection, get_channel, close_rabbitmq, persistence

connection = get_connection()
channel = get_channel(connection)

channel.queue_declare(queue='ResultQueue', durable=True)
channel.exchange_declare(exchange='ResultExchange', exchange_type='direct', durable=True)
channel.queue_bind(exchange='ResultExchange', queue='ResultQueue', routing_key='Result')


def push_message(message):
    print(message)
    channel.basic_publish(
        exchange='ResultExchange',
        routing_key='Result',
        body=json.dumps(message),
        properties=persistence
    )
    close_rabbitmq(connection, channel)
