# -*- coding: utf-8 -*-*
from twisted.internet.protocol import DatagramProtocol
import c2w
from c2w.main.lossy_transport import LossyTransport
import logging
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')

import time
from c2w.main.constants import ROOM_IDS

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
        
        self.seq_number = 0 #This variable contains the sequence number used to track packet loss
        self.userID = 0 #This vatiable contains the id of the client that was set by the server (initially set to 0)
        self.lastEventID = 0 #This variable contains the id of the last event the client is currently aware of.
        self.userRoomID = 0 #This variable contains the room the client is currently in.
        self.futureRoomID = 0 #This variable contains the room the client want to switch to
        self.entry_number_awaited = 0 #This variable contains the number of entry the client is expecting from the next multi-entry response
        
        self.packet_stored = 0 #This variable contains a packet to be resent if its answer is not received. When it is equals to 0 there is no packet to resend.
        self.packet_awaited = 16 #This variable contains the type of the next packet to be received. When it is equals to 16 there is no packet to be received.
              
        self.store = c2wClientModel() #The c2wClientModel is a class used to store all data about users and movies
        
        self.delay = 0.5 #The length of the timer that is armed whenever the client send a request. When it runs out the client resend the message if no answer was given.
        self.pingTimer = 1 #The time to wait before sending a ping after having received last pong
        self.resendTries = 0 #The number of times the resend function has resent the message
        
        
    def startProtocol(self):
        """one_user_full_login_udp_server_test
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.packet_stor
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport
        self.store.addMovie(ROOM_IDS.MAIN_ROOM, '0.0.0.0', '0', 0)


########### The function that resends packets whenever the timer runs out.
    #OK
    def resend_packet(self, seq_number):
        if self.packet_awaited != 16 and self.packet_stored != 0 and self.seq_number == seq_number: #Check if there is a packet to be resent
            if self.resendTries < 10 :
                print('resending :')
                print(self.packet_stored)
                self.transport.write(self.packet_stored, (self.serverAddress, self.serverPort))
                self.resendTries += 1
                reactor.callLater(self.delay, self.resend_packet, seq_number)
                              


########### PUT_LOGIN  
    #OK
    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
               
        moduleLogger.debug('loginRequest called with username=%s', userName)
        packet = packing.PUT_LOGIN(self.seq_number,userName)    
        print('login :')
        print(packet)
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 1
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)


########### PUT_NEW_MESSAGE    
    #OK
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
        
        moduleLogger.debug('Message request called with content=%s', message)
        packet = packing.PUT_NEW_MESSAGE(self.seq_number,self.userID,self.userRoomID,message)
        print('new message :')
        print(packet)     
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 15
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)
        

########### PUT_SWITCH_ROOM     
    #OK
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
        
        moduleLogger.debug('Join Room request called with room name = %s', roomName)
        
        self.futureRoomID = self.store.getMovieByTitle(roomName).movieId
        print('put switch room :')
        print(packet)
        packet = packing.PUT_SWITCH_ROOM(self.seq_number, self.userID, self.futureRoomID)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))
        
        self.packet_stored = packet
        self.packet_awaited = 13
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)
        

########### PUT_LOGOUT     
    #OK
    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        
        moduleLogger.debug('Leave system request called')
        
        packet = packing.PUT_LOGOUT(self.seq_number,self.userID)
        print('logout :')
        print(packet)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 3
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)
        

########### GET_PING     
    #OK
    def sendGetPingRequestOIE(self):
        """
        This function is used by the chatClientProtocol to get ping from the server
        """
        
        moduleLogger.debug('Get ping request called')
        
        packet = packing.GET_PING(self.seq_number,self.userID,self.lastEventID,self.userRoomID)      
        print('get_ping :')
        print(packet)
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 5
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)
        

########### GET_EVENTS     
    #OK
    def sendGetEventsRequestOIE(self,nbr_events):
        """
        This function is used by the chatClientProtocol when a ping from the server has revealed that the client is not synchronized yet
        """
        
        moduleLogger.debug('Get events request called')
        
        self.entry_number_awaited = nbre_events
        packet = packing.GET_EVENTS(self.seq_number, self.userID, self.lastEventID, nbr_events, 0)
        print('get events :')
        print(packet)
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 7
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)


########### GET_ROOMS   
    #OK
    def sendGetRoomsRequestOIE(self,first_room_id, nbr_rooms):
        """
        This fuction is used by the chatClientProtocol to get a list of current rooms
        """
        
        moduleLogger.debug('Get rooms request called')
        
        self.entry_number_awaited = nbr_rooms
        packet = packing.GET_ROOMS(self.seq_number, self.userID, first_room_id, nbr_rooms)      
        print('get rooms :')
        print(packet)
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 9
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)

########### GET_USERS    
    #OK
    def sendGetUsersRequestOIE(self,first_user_id, nbr_users):
        """
        This function is used by the chatClientProtocol to get a list of current users
        """
        
        moduleLogger.debug('Get users request called')
        
        self.entry_number_awaited = nbr_users
        packet = packing.GET_USERS(self.seq_number, self.userID, first_user_id, nbr_users, self.userRoomID)      
        print('get_users :')
        print(packet)
        self.transport.write(packet, (self.serverAddress, self.serverPort))

        self.packet_stored = packet
        self.packet_awaited = 11
        reactor.callLater(self.delay, self.resend_packet, self.seq_number)
                

###########      
               
    def datagramReceived(self, datagram, host_port):

        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """

        fieldsList = unpacking.decode(datagram)
        print(fieldsList)
        
        if fieldsList[0][0] == self.packet_awaited and fieldsList[0][1] == self.seq_number :
            #Check if the message received is the one that is awaited (type and sequence number check)
            print('packet received')
            self.packet_stored = 0
            self.packet_awaited = 16
            self.resendTries = 0
            self.seq_number += 1
            
            moduleLogger.debug('Expected response received, decoding...')
            ########### RESPONSE_LOGIN OK
            if fieldsList[0][0] == 1 :          
                print('login resp rec')
                if fieldsList[1][0] == 0 :                    
                    print('Login status : Done')
                    self.userID = fieldsList[1][1]
                    self.lastEventID = fieldsList[1][2]
                    self.sendGetUsersRequestOIE(1, 255)
                elif fieldsList[1][0] == 1 :
                    self.clientProxy.connectionRejectedONE('Unknow error')
                    print('Login status : Unknown error')
                elif fieldsList[1][0] == 2 :
                    self.clientProxy.connectionRejectedONE('Too many users')
                    print('Login status : Too many users')
                elif fieldsList[1][0] == 3 :
                    self.clientProxy.connectionRejectedONE('Invalid username')
                    print('Login status : Invalid username')
                elif fieldsList[1][0] == 4 :
                    self.clientProxy.connectionRejectedONE('Username not available')
                    print('Login status : Username not available')
            
                                     
            ########### RESPONSE_LOGOUT                
            if fieldsList[0][0] == 3 :
                print('logout resp rec')
                self.userID = 0
                self.lastEventID = 0
                self.seq_number = 0
                self.packet_stored = 0
                self.packet_awaited = 16
                self.store.removeAllMovies()
                self.store.removeAllUsers()
                self.clientProxy.leaveSystemOKONE()
                moduleLogger.debug('Logout status : Done')
            
                    
            ########### RESPONSE_PING
            elif fieldsList[0][0] == 5 :
                print('ping resp rec')
                lastServerEventID = fieldsList[1][0]
                if self.lastEventID != lastServerEventID :
                    moduleLogger.debug('Ping status : Not up-to-date, getting events required')
                    self.sendGetEventsRequestOIE(lastServerEventID - lastEventID)
                    
                else :
                    moduleLogger.debug('Ping status : up-to-date, preparing next ping')
                    reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE)
                    
            
                
            ########### RESPONSE_EVENTS        
            elif fieldsList[0][0] == 7 :
                print('events resp rec')
                n = 0
                for i in range(len(fieldsList[1])):
                    n += 1
                    if fieldsList[1][i][1] == 1 : #Message event
                        print('message !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        user = self.store.getUserById(fieldsList[1][i][3])
                        if user.userChatRoom == self.userRoomID :
                            self.clientProxy.chatMessageReceivedONE(user.userName, fieldsList[1][i][4])
                            moduleLogger.debug('GetEvents status : New message available')
                        
                    elif fieldsList[1][i][1] == 2 : #New user event
                        print('newser !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        room = self.store.getMovieByID(fieldsList[1][i][2]).movieTitle
                        self.store.addUser(fieldsList[1][i][4], fieldsList[1][i][3], room)
                        self.clientProxy.userUpdateReceivedONE(fieldsList[1][i][4], room)
                        moduleLogger.debug('GetEvents status : New user')
                        
                    elif fieldsList[1][i][1] == 3 : #Switch room event
                        print('switchi !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        name = self.store.getUserByID(fieldsList[1][i][3]).userName
                        room = self.store.getMovieByID(fieldsList[1][i][4]).movieTitle
                        self.store.updateUserChatroom(name, fieldsList[1][i][4])
                        self.clientProxy.userUpdateReceivedONE(name, room)
                        moduleLogger.debug('GetEvent status : User switched room')
                    
                    elif fieldsList[1][i][1] == 4 : #Logout event
                        print('disco !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        name = self.store.getUserByID(fieldsList[1][i][3]).userName
                        self.store.removeUser(name)
                        self.clientProxy.userUpdateReceivedONE(name, ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM)
                        moduleLogger.debug('GetEvent status : User logged out')
                        
                if n < self.entry_number_awaited and n !=0 :
                    print('GetEvent status : Asking for more events')
                    self.sendGetEventsRequestOIE(self.entry_number_awaited - n)
                    
                else :
                    print('GetEvent status : up-to-date, preparing next ping')
                    reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE)
                    
            
                    
            ########### RESPONSE_ROOMS
            elif fieldsList[0][0] == 9 :
                print('rooms resp rec')
                #FieldsList returns the data in the following form : Room_id, IP, Port, Room_name, Nbr_users
                #AddMovie accepts it in the following form : Title, IP, Port, ID 
                n = 0
                moduleLogger.debug('Room status : Rooms list received')
                for i in range(len(fieldsList[1])):
                    n += 1
                    if self.store.getMovieById(fieldsList[1][i][0]) == None :   
                        self.store.addMovie(fieldsList[1][i][3], fieldsList[1][i][1], fieldsList[1][i][2], fieldsList[1][i][0], fieldsList[1][i][4])
                
                if n < self.entry_number_awaited and n !=0 :
                    print('Room status : Asking for more rooms')
                    self.sendGetRoomsRequestOIE(n, self.entry_number_awaited - n)
                    
                else : 
                    movieList = self.store.getMovieList() #get the movie list in the appropriate format
                    for i in range(1, len(movieList)) :
                        movieList[i] = (movieList[i].movieTitle, movieList[i].movieIpAdress, movieList[i].moviePort)
                
                    userList = store.getUserList() #get the user list in the appropriate format
                    for i in range(len(userList)) :
                        room = self.store.getMovieByID(userList[i].userChatRoom).movieTitle
                        userList[i] = (userList[i].userName, room)
                    self.clientProxy.initCompleteONE(userList, movieList) #send both to the UI
                    print('Room status : UI has been updated')
                    
                    print('Room status : UI is ready, starting ping cycle')
                    self.sendGetPingRequestOIE() #Then starts the Ping - Pong - GetEvents - ResponseEvents - Ping cycle
                    
                                   

            ########### RESPONSE_USERS
            elif fieldsList[0][0] == 11 :
                print('users resp rec')
                n = 0
                #FieldsList returns the data in the following form : user_id, user_name, room_id
                #AddUser accepts it in the following form : Name, ID, Chatroom
                moduleLogger.debug('Users status : Users list received')
                for i in range(1, len(fieldsList[1])):
                    n += 1
                    if self.store.getUserById(fieldsList[1][i][0]) == None :
                        self.store.addUser(fieldsList[1][i][1], fieldsList[1][i][0], fieldsList[1][i][2])
                        
                if n < self.entry_number_awaited and n !=0 :
                    print('Users status : Asking for more users')
                    self.sendGetRoomsRequestOIE(n, self.entry_number_awaited - n)
                else :
                    print('Users status : Users list fully updated, asking for rooms')
                    self.sendGetRoomsRequestOIE(1, 255)
            
                
            ########### RESPONSE_SWITCH_ROOM
            elif fieldsList[0][0] == 13 :
                print('switch resp rec')
                if fieldsList[1][0] == 0 :
                    self.clientProxy.joinRoomOKONE()
                    self.userRoomID = self.futureRoomID
                    print('Switch room status : Done')
                elif fieldsList[1][0] == 1 :
                    print('Switch room status : Unknow error')
            
            
            ########### RESPONSE_NEW_MESSAGE
            elif fieldsList[0][0] == 15 :
                print('new message resp rec')
                if fieldsList[1][0] == 0 :
                    print('Message status : transmitted')
                elif fieldsList[1][0] == 1 :
                    print('Message status : Unknown error')
                    self.clientProxy.chatMessageReceivedONE('Server', 'Message status : Unknown error')
                elif fieldsList[1][0] == 2 :
                    print('Message status : Invalid room')
                    self.clientProxy.chatMessageReceivedONE('Server', 'Message status : Invalid room')
                elif fieldsList[1][0] == 3 :
                    print('Message status : Incorrect room (You must send a message only into your current room)')
                    self.clientProxy.chatMessageReceivedONE('Server', 'Message status : Incorrect room (You must send a message only into your current room)')             

###########
