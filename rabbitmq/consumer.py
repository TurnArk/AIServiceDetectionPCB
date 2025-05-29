from public.channel import get_channel,get_connection,close_rabbitmq
from service.model_service import service
import json

connection = get_connection()
channel = get_channel(connection)

channel.declare_queue('RequestQueue', durable=True)
channel.declare_exchange('RequestExchange', exchange_type='direct', durable=True)
channel.queue_bind(exchange='RequestExchange', queue='RequestQueue', routing_key='Request')


def callback(ch, method, properties, body):
    result = json.loads(body.decode('utf-8'))
    service(result)
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(
    queue='RequestQueue',
    on_message_callback=callback,
    auto_ack=False
)

channel.start_consuming()