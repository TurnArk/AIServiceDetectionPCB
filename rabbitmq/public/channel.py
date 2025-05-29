import pika


def get_connection():
    user = pika.PlainCredentials('ark', 'alice')
    return pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, 'gundam', user))


def get_channel(connect):
    return connect.channel()


def close_rabbitmq(connection, channel):
    channel.close()
    connection.close()


persistence = pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)