#!/usr/bin/env python
import pika
from rmq_params import rmq_params


Exchange = rmq_params["exchange"]
print (Exchange)

print ("establishing credentials")
credentials = pika.PlainCredentials('brendan', 'admin')
print ("establishing connection params")
parameters = pika.ConnectionParameters(credentials=credentials, host='172.30.91.242')
print ("attempting to connect")
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

queues = []
for queue in rmq_params["queues"]:
    queues.append(queue)
    #on startup must purge and unbind the queues
    channel.queue_purge(queue)
    channel.queue_unbind(queue)

channel.exchange_declare(exchange=Exchange, exchange_type='direct')

for q in queues:
    channel.queue_declare(queue=q)
    channel.queue_bind(q, Exchange)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback,
                      queue='hello',
                      no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
