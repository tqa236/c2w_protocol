# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
from . import unpacking
from . import packing
import c2w.main.constants.ROOM_IDS

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        self.serverProxy = serverProxy
        self.lossPr = lossPr
        self.clientList = []
        self.seq_numberList = []
        self.last_event_ID = 0
        #self.main_room = self.serverProxy

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        
        fieldsList = unpacking.decode(datagram)
        if fieldsList[0][0] == 0 : #Le message reçu est de type PUT_LOGIN, user_id = 0 par definition car le client attends que l'on lui en attribue une
            new_username = fieldsList[1][0]
            self.seq_numberList.append(fieldsList[0][1])
            #main_room = c2w.main.constants.ROOM_IDS.MAIN_ROOM()
            user_id = self.serverProxy.addUser(new_username,'main_room')
            packet = RESPONSE_LOGIN.RESPONSE_LOGIN(fieldsList[0][1],user_id,new_username,self.clientList,0,0)
            self.clientList.append((user_id, new_username))
            self.transport.write(packet, host_port)
