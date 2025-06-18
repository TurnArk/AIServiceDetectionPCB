import json
import time
from public.channel import get_connection, get_channel, close_rabbitmq, persistence




def connect():
    for attempt in range(3, 0, -1):
        try:
            connection = get_connection()
            channel = get_channel(connection)

            channel.queue_declare(queue='ResultQueueOne', durable=True)
            channel.queue_declare(queue='ResultQueueTwo', durable=True)
            channel.exchange_declare(exchange='ResultExchange', exchange_type='fanout', durable=True)
            # 将队列绑定到 Fanout 交换机（Fanout 不需要 routing_key）
            channel.queue_bind(exchange='ResultExchange', queue='ResultQueueOne')
            channel.queue_bind(exchange='ResultExchange', queue='ResultQueueTwo')

            return connection, channel
        except Exception as e:
            print(f"连接失败，剩余重试次数: {attempt-1}，错误: {e}")
            if attempt == 1:
                raise RuntimeError("无法连接到 RabbitMQ 服务器") from e
            time.sleep(5)


def push_message(message):
    connection, channel = connect()
    print(message)
    channel.basic_publish(
        exchange='ResultExchange',
        routing_key='',
        body=json.dumps(message),
        properties=persistence
    )
    close_rabbitmq(connection, channel)
