from public.channel import get_channel,get_connection,close_rabbitmq
from service.model_service import service
import json

print("已启动服务")

connection = get_connection()
channel = get_channel(connection)

channel.queue_declare('RequestQueue', durable=True)
channel.exchange_declare('RequestExchange', exchange_type='direct', durable=True)
channel.queue_bind(exchange='RequestExchange', queue='RequestQueue', routing_key='Request')


def callback(ch, method, properties, body):
    try:
        result = json.loads(body.decode('utf-8'))
        print(f"启用回调，开始处理。\n{result}")
        service(result)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except  Exception as e:
        print(f"处理失败：{e}")



channel.basic_consume(
    queue='RequestQueue',
    on_message_callback=callback,
    auto_ack=False
)

channel.start_consuming()