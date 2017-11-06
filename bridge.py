#!/usr/bin/env python
from bluetooth import *
import pika
from rmq_params import rmq_params
import sys
from pymongo import MongoClient
import time

# function to send a string to the bluetooth device
# INPUT: string to send, and client socket
def blueSend(sendString, client_sock):
    client_sock.send(sendString)

# function to return a string that was received from the bluetooth device
# INPUT: the bluetooth server_socket
def blueReceive(client_sock, client_add):
    gots = ''
    data = ''
    while(data != b'\n' and is_valid_address(client_add)):
        data = client_sock.recv(1024)
        if(data == b' '):
            gots += ' '
        else:
            gots += data.strip().decode('ascii')

    blueSend('\n', client_sock)
    return gots

# Equivalent of main entry point below here:
vhost = rmq_params["vhost"]
username = rmq_params["username"]
password = rmq_params["password"]
exchange = rmq_params["exchange"]
queues = rmq_params["queues"]

ip = sys.argv[1]
print("ip: [%s]" % ip)

credentials = pika.PlainCredentials(username, password)
print("valid credentials")
parameters = pika.ConnectionParameters(credentials = credentials, host = ip)
print("valid parameters")
connection = pika.BlockingConnection(parameters)

mongoClient = MongoClient()
db = mongoClient.exchange

print("[Checkpoint 01] Connected to database %s on MongoDB server at 'local host'" % (db))
channel = connection.channel()
print("[Checkpoint 02] Connected to vhost %s on RMQ server at %s as user %s" % (vhost, ip, username))

# Bluetooth overhead
server_sock=BluetoothSocket( RFCOMM )
#server_sock.setsockopt(server_sock.SOL_SOCKET, server_sock.SO_REUSEADDR, 1)
server_sock.bind(("",1))
server_sock.listen(1)
port = server_sock.getsockname()[1]

print("[Checkpoint 03] Created RFCOMM bluetooth socket on port %s" % port)

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ]
                    )

client_sock, client_info = server_sock.accept()
print("[Checkpoint 04] Accepted RFCOMM bluetooth connection from  ", client_info)
print("Simulate LED green flash")
blueSend('\n\n', client_sock)
blueSend('Communicating on exchange %s' % exchange, client_sock)
blueSend('\n', client_sock)
blueSend('Available queues are: %s' % queues, client_sock)

def callback(ch, method, properties, body):
    print('[Checkpoint c-01] Consumed a message published with routing_key: %s' % method.routing_key)
    print('[Checkpoint c-02] Message: %s' % body)
    print('[Checkpoint c-03] Sending to RFCOMM bluetooth client')
    blueSend(body, client_sock)

clientAdd = client_info[0]

post = blueReceive(client_sock, clientAdd)
while(is_valid_address(clientAdd)):
    if(post[0] == 'p'):
        #publish command
        temp = post.split(':')[1]
        tempQueue = temp.split(' ')[0]
        message = temp.split('"')[1]
        print("tempQueue is: [%s]" % tempQueue)
        print("Message is: [%s]" % message)
        if(tempQueue == 'Q_1' or tempQueue == 'Q_2' or tempQueue == 'Q_3'):
            channel.basic_publish(exchange=exchange,
                              routing_key=tempQueue,
                              body=message)
            ticks = time.time()
            msgID = "14"+"$"+str(ticks)
            obj = {
                "Action": "p",
                "Place": exchange,
                "MsgID": msgID,
                "Subject": tempQueue,
                "Message": message
            }
            clltempQueue = db.libs
            clltempQueue.insert(obj)

        else:
            blueSend('Invalid message queue\n')
    elif(post[0] == 'c'):
        #consume command
        tempQueue = post.split(':')[1]
        channel.basic_consume(callback, queue=tempQueue, no_ack=True)

    elif(post[0] == 'h'):
        #history
         clltempQueue = db.libs
         print('[Checkpoint h-01] Printing history of collection %s in MongoDB database %s' % (db.collection_names()[1], exchange))
         for el in clltempQueue.find():
             print(el)
    else:
        print('Invalid input. Try again NOOB')

    post=blueReceive(client_sock, clientAdd)

# VERY END
client_sock.close()
server_sock.close()
