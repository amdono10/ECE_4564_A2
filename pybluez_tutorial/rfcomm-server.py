# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import *

def blueReceive(client_sock):
    gots = ''
    data = ''
    while(data != b'\n'):
        data = client_sock.recv(1024)
        if(data == b' '):
            gots += ' '
        else:
            gots += data.strip().decode('ascii')
    return gots

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ]
                    )

print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)
clientAdd = client_info[0]
print("client Address = %s" % clientAdd)

try:
    tests = ''
    data = ''
    while(is_valid_address(clientAdd)):
        post = blueReceive(client_sock)
        #print("post is [%s]" % post)
        if(post[0] == 'p'):
            #publish command
            temp = post.split(':')[1]
            tempQueue = temp.split(' ')[0]
            message = temp.split('"')[1]
            print("tempQueue is: [%s]" % tempQueue)
            print("Message is: [%s]" % message)
except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")
