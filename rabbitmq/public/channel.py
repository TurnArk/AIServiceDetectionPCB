import pika


def get_connection():
    user = pika.PlainCredentials('ark', 'alice')
    return pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost',
        port=5672,
        virtual_host='gundam',
        heartbeat=30,
        blocked_connection_timeout=3000,
        credentials=user
    ))


def get_channel(connect):
    return connect.channel()


def close_rabbitmq(connection, channel):
    channel.close()
    connection.close()


persistence = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)