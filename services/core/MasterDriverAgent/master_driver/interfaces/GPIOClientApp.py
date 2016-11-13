import socket
import sys

HOST , PORT = "192.168.1.3",9999

REQUEST = "IsMotionDetect"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    sock.sendto(REQUEST + '\n',(HOST,PORT))
    print "Send Request"
    received = sock.recv(255)
    print "Sent: {}".format(REQUEST)
    print "Received {}".format(received)
