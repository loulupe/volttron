#This code has been developed for the 1st PNNL Connected Building Challenge
#by the team "Ventilation Scheduler"
#All our development is based on opensource contributions
#It is intended to be distributed for the building automation communities for research and educational purposes
#Copyrights and license is to be determined
#This work is being funded by the Department of Energy Program - BIRD Building Integration Research and Developed Innovators Program
#and NSF-I-Corps - Rochester Institute of Technology.
#None of the team members, entities that had collaborated or funded to this project has legal liability 
#or responsibility for any outcome
#The views and opinions of any team member or collaborator do not reflect those of any agencyentity.
#_Project Team: Lourdes Gutierrez and Priyank Kapadia
#_Contact info: lmg4630@rit.edu, plk8075@rit.edu
#_Created: 2016-06-19

import socket
import sys

HOST , PORT = "192.168.1.4",9999
#change the IP address, look on the terminal for your IP address by typing ifconfig
#choose your port, it can be any number

REQUEST = "IsMotionDetect"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    sock.sendto(REQUEST + '\n',(HOST,PORT))
    print "Send Request"
    received = sock.recv(100)

    print "Sent: {}".format(REQUEST)
    print "Received {}".format(received)
