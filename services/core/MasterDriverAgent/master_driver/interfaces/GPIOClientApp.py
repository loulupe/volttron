import socket
import sys

HOST , PORT = "192.168.1.4",9999

REQUEST = "IsMotionDetect"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    sock.sendto(REQUEST + '\n',(HOST,PORT))
    print "Send Request"
    received = sock.recv(100)

    print "Sent: {}".format(REQUEST)
    print "Received {}".format(received)
