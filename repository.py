#!/usr/bin/env python
import pika
import time
from rmq_params import rmq_params

Exchange = rmq_params["exchange"]
master = rmq_params["master_queue"]
status = rmq_params["status_queue"]

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

channel.exchange_declare(exchange=Exchange, exchange_type='direct')

#bind the master queue to the exchange
channel.queue_declare(queue=master)
channel.queue_bind(master, Exchange)
channel.queue_purge(master)

#bind the status queue
channel.queue_declare(queue=status)
channel.queue_bind(status, Exchange)
channel.queue_purge(status)

for q in queues:
    channel.queue_declare(queue=q)
    channel.queue_bind(q, Exchange)
    channel.queue_bind(master, Exchange, q)
    channel.queue_purge(q)


def callback(ch, method, properties, body):
    print(" [3] Consumed a message with routing key: %s " % method.routing_key)
    print(" [4] Message: %s" % body)
    time.sleep(2)
    print(" [x] Flashing LED Purple")

channel.basic_consume(callback,queue=master,no_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
