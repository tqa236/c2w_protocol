# -*- coding: utf-8 -*-*
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')

import time

from . import unpacking
from . import packing

from twisted.internet import reactor
from c2w.main.client_model import c2wClientModel


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        
        self.seq_number = 0
        self.userID = 0
        self.lastEventID = 0
        self.userRoomID = 0
        
        self.packet_stored = 0 #This variable contains a packet to be resent if its answer is not received. When it is equals to 0 there is no packet to resend.
        self.packet_awaited = 16 #This variable contains the type of the next packet to be received. When it is equals to 16 there is no packet to be received.
              
        self.store = c2wClientModel() #The c2wClientModel is a class used to store information about users and movies
        
        self.delay = 0.5 #500ms
        self.nbr_rooms = 50 # numéro de rooms que le client va demander en chaque GET_ROOMS
        self.nbr_users = 50 # numéro de users que le client va demander en chaque GET_USERS
        
        
    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
        
########### PUT_LOGIN  
   
    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGIN packet to the server
        # - Re-emit it if the timer ran out
               
        moduleLogger.debug('loginRequest called with username=%s', userName)
        packet = packing.PUT_LOGIN(self.seq_number,userName)        
              
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 2
        reactor.callLater(self.delay, self.resend_packet)

########### The function which resend any request that needs to be

    def resent_packet(self):
    
        if packet_awaited != 16 and packet_stored != 0 : #Check of there is a packet to be resent
            self.transport.write(self.packet_stored, (self.serverAddress, self.serverPort))
            reactor.callLater(self.delay, self.resend_packet)   
                     
########### PUT_NEW_MESSAGE    
   
    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_NEW_MESSAGE packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Message request called with content=%s', message)
        packet = packing.PUT_NEW_MESSAGE = (self.seq_number,self.userID,self.userRoomID,message)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 15
        reactor.callLater(self.delay, self.resend_packet)
        

########### PUT_SWITCH_ROOM     
   
    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_SWITCH_ROOM with the roomName field packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Join Room request called with room name = %s', roomName)
        
        RoomID = store.getMovieByTitle(roomName).movieId; # Je ne suis pas sûr si movieId est dejà une integer, il faut conférer ça.
        packet = packing.PUT_SWITCH_ROOM = (self.seq_number,self.userID,RoomID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 13
        reactor.callLater(self.delay, self.resend_packet)
        

########### PUT_LOGOUT     
   
    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Leave system request called')
        
        packet = packing.PUT_LOGOUT = (self.seq_number,self.userID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 3
        reactor.callLater(self.delay, self.resend_packet)
        

########### GET_PING     
   
    def sendGetPingRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Get ping request called')
        
        packet = packing.GET_PING = GET_PING(self.seq_number,self.user_ID,self.lastEventID,self.userRoomID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 5
        reactor.callLater(self.delay, self.resend_packet)
        

########### GET_EVENTS     
   
    def sendGetEventsRequestOIE(self,nbr_events):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Get events request called')
        
        packet = packing.GET_EVENTS = (self.seq_number,self.userID,nbr_events,self.userRoomID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 7
        reactor.callLater(self.delay, self.resend_packet)


########### GET_ROOMS     
   
    def sendGetRoomsRequestOIE(self,first_room_id):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Get rooms request called')
        
        packet = packing.GET_ROOMS = (self.seq_number,self.userID,first_room_id,self.nbr_rooms)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 9
        reactor.callLater(self.delay, self.resend_packet)

########### GET_USERS     
   
    def sendGetUsersRequestOIE(self,first_user_id):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        
        moduleLogger.debug('Get users request called')

        packet = packing.GET_USERS = (self.seq_number,self.userID,first_user_id,self.nbr_users,self.userRoomID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 11
        reactor.callLater(self.delay, self.resend_packet)
                

###########      
               
    def datagramReceived(self, datagram, host_port):

        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """

        #This function should :
        # - Unpack the datagram
        # - Read the  SEQ_NUMBER and MESSAGE_TYPE fields in the header
        # - If the SEQ_NUMBER is the one that is awaited, proceed, if not stop right there
        # - Disarm the timer that was armed with the last sendRequest
        # - Select the correct following function to read the unpacked datagram based on MESSAGE_TYPE field


        fieldsList = unpacking.decode(datagram)
        
        #if fieldsList[0][1] in self.packets_sent: #Le message reçu est attendu
        #    del self.packets_sent[fieldsList[0][1]] # On supprime the packet from the packet list to resend
        
        
        if fieldsList[0][0] == self.packet_awaited and fieldsList[0][1] == self.seq_number :
            #Verification que le message reçu est celui qui est attendu
            self.packet_stored = 0
            self.packet_awaited = 16
            self.seq_number += 1
            
            ########### RESPONSE_LOGIN
            if fieldsList[0][0] == 1 : #Le message reçu est de type RESPONSE_LOGIN            
                       
                if fieldsList[1][0] == 0 : #Status code = success
                    self.userID = fieldsList[1][1]
                    self.lastEventID = fieldsList[1][2]
                elif fieldsList[1][0] == 1 :
                    self.clientProxy.connectionRejectedONE('Unknow error')
                elif fieldsList[1][0] == 2 :
                    self.clientProxy.connectionRejectedONE('Too many users')
                elif fieldsList[1][0] == 3 :
                    self.clientProxy.connectionRejectedONE('Invalid username')
                elif fieldsList[1][0] == 4 :
                    self.clientProxy.connectionRejectedONE('Username not available')
                else :
                    self.clientProxy.connectionRejectedONE('Impossible to interpret RESPONSE_LOGIN');
                                     
            ########### RESPONSE_LOGOUT                
            if fieldsList[0][0] == 3 : #Le message reçu est de type RESPONSE_LOGOUT
                self.userID = 0
                self.lastEventID = 0
                self.seq.number = 0
                self.packet_stored = 0
                self.packet_awaited = 16
                self.store.removeAllMovies()
                self.store.removeAllUsers()
                    
            ########### RESPONSE_PING
            elif fieldsList[0][0] == 5 : #Le message reçu est de type RESPONSE_PING
                pass
                
            ########### RESPONSE_EVENTS        
            elif fieldsList[0][0] == 7 : #Le message reçu est de type RESPONSE_EVENTS
                pass
                    
            ########### RESPONSE_ROOMS
            elif fieldsList[0][0] == 9 : #Le message reçu est de type RESPONSE_ROOMS
                
                for i in range(len(fieldsList)-1):
                    if store.getMovieById(fieldsList[1+i][0]) == None:   
                        store.addMovie(fieldsList[1+i][3],fieldsList[1+i][1], fieldsList[1+i][2], fieldsList[1+i][0],fieldsList[1+i][4]);
                        #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users                

            ########### RESPONSE_USERS
            elif fieldsList[0][0] == 11 : #Le message reçu est de type RESPONSE_USERS
                pass
                
            ########### RESPONSE_SWITCH_ROOM
            elif fieldsList[0][0] == 13 : #Le message reçu est de type RESPONSE_SWITCH_ROOM
                if fieldsList[1][0] == 0 : #Status code = success
                    self.clientProxy.connectionRejectedONE('Change room succesful'); ###################### pas la bonne fonction
                elif fieldsList[1][0] == 1 :
                    self.clientProxy.connectionRejectedONE('Unknow error');
                else :
                    self.clientProxy.connectionRejectedONE('Impossible to interpret RESPONSE_SWITCH_ROOM'); 
                    
            ########### RESPONSE_NEW_MESSAGE
            elif fieldsList[0][0] == 15 : #Le message reçu est de type RESPONSE_NEW_MESSAGE
                if fieldsList[1][0] == 0 : #Status code = success
                    self.clientProxy.connectionRejectedONE('The message was well transmitted'); ###################### pas la bonne fonction
                elif fieldsList[1][0] == 1 :
                    self.clientProxy.connectionRejectedONE('Unknow error');
                elif fieldsList[1][0] == 2 :
                    self.clientProxy.connectionRejectedONE('Invalid room (not in the system)');
                elif fieldsList[1][0] == 3 :
                    self.clientProxy.connectionRejectedONE('Incorrect room (You must send a message only into your current room)');
                else :
                    self.clientProxy.connectionRejectedONE('Impossible to interpret RESPONSE_NEW_MESSAGE');                

########### 
        
###########     
    
                     
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
