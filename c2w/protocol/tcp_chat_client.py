# -*- coding: utf-8 -*-*
from twisted.internet.protocol import DatagramProtocol
import c2w
import logging
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')

import time
from c2w.main.constants import ROOM_IDS

from . import unpacking
from . import packing
from . import tcp_reception

from twisted.internet import reactor
from c2w.main.client_model import c2wClientModel


class c2wTcpChatClientProtocol(DatagramProtocol):

    def __init__(self, clientProxy, serverAddress, serverPort):

        """
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.

        :param serverPort: The port number used by the c2w server,
            given by the user.

        Class implementing the UDP version of the client protocol.

        .. note::

            You must write the implementation of this class.

        Each instance must have at least the following attribute:


        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number used by the c2w server.

        .. note::

            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number used by the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.frame = b'' #The buffer where all the data received but not decoded yet is stocked
        self.clientProxy = clientProxy
        self.seq_number = 0 #This variable contains the sequence number used to send packet
        self.userID = 0 #This vatiable contains the id of the client that was set by the server (initially set to 0)
        self.lastEventID = 0 #This variable contains the id of the last event the client is currently aware of.
        self.userRoomID = 0 #This variable contains the room the client is currently in.
        self.futureRoomID = 0 #This variable contains the room the client want to switch to
        
        self.packet_awaited = 16 #This variable contains the type of the next packet to be received. When it is equals to 16 there is no packet to be received.
              
        self.store = c2wClientModel() #The c2wClientModel is a class used to store all data about users and movies
        
        self.pingTimer = 1 #The time to wait before sending a ping after having received last pong
        self.store.addMovie(ROOM_IDS.MAIN_ROOM, '0.0.0.0', '0', 0)
        


    def connectionLost(self, reason) :
        """
        The connection with the server was lost  because of the reason given in arg
        """
        print('connection lost : ' + str(reason))


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
        self.transport.write(packet)
        
        self.packet_stored = packet
        self.packet_awaited = 1


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
        self.transport.write(packet)
        
        self.packet_stored = packet
        self.packet_awaited = 15
        

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
        packet = packing.PUT_SWITCH_ROOM(self.seq_number, self.userID, self.futureRoomID)
        print('put switch room :')
        print(packet)    
        self.transport.write(packet)
        
        self.packet_stored = packet
        self.packet_awaited = 13
        

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
        self.transport.write(packet)

        self.packet_stored = packet
        self.packet_awaited = 3
        

########### GET_PING     
    #OK
    def sendGetPingRequestOIE(self):
        """
        This function is used by the chatClientProtocol to get ping from the server
        """
        
        if self.packet_awaited == 16 : #Check if there is an awaited response first, if not start the ping
            moduleLogger.debug('Get ping request called')
            packet = packing.GET_PING(self.seq_number,self.userID,self.lastEventID,self.userRoomID)      
            print('get_ping :')
            print(packet)
            self.transport.write(packet)
            self.packet_stored = packet
            self.packet_awaited = 5

        else : #If there is, report the ping at a later date (to make sure there is never two requests sent by the client and not answered at once)
            reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE)
            
########### GET_EVENTS     
    #OK
    def sendGetEventsRequestOIE(self,nbr_events):
        """
        This function is used by the chatClientProtocol when a ping from the server has revealed that the client is not synchronized yet
        """
        
        moduleLogger.debug('Get events request called')
        packet = packing.GET_EVENTS(self.seq_number, self.userID, self.lastEventID, nbr_events, 0)
        print('get events :')
        print(packet)
        self.transport.write(packet)

        self.packet_stored = packet
        self.packet_awaited = 7


########### GET_ROOMS   
    #OK
    def sendGetRoomsRequestOIE(self,first_room_id, nbr_rooms):
        """
        This fuction is used by the chatClientProtocol to get a list of current rooms
        """
        
        moduleLogger.debug('Get rooms request called')
        packet = packing.GET_ROOMS(self.seq_number, self.userID, first_room_id, nbr_rooms)      
        print('get rooms :')
        print(packet)
        self.transport.write(packet)

        self.packet_stored = packet
        self.packet_awaited = 9

########### GET_USERS    
    #OK
    def sendGetUsersRequestOIE(self,first_user_id, nbr_users):
        """
        This function is used by the chatClientProtocol to get a list of current users
        """
        
        moduleLogger.debug('Get users request called')
        packet = packing.GET_USERS(self.seq_number, self.userID, first_user_id, nbr_users, self.userRoomID)      
        print('get_users :')
        print(packet)
        self.transport.write(packet)

        self.packet_stored = packet
        self.packet_awaited = 11
                

###########      
               
    def dataReceived(self, data):
        """
        :param data: The data received from the server (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """
        
        print('Data received')
        self.frame = self.frame + data
        complet, longueur = tcp_reception.framing(self.frame)
        if complet :
            datagram = self.frame[:longueur] #The datagram received is of this length according to the header
            print('A full packet has been received :')
            fieldsList = unpacking.decode(datagram)
            print(fieldsList)
            self.frame = self.frame[longueur:] #After decoding the datagram, we delete it from the buffer
            self.seq_number += 1
            self.packet_awaited = 16 #Set the packet_awaited to 16, allowing pings.
            if len(self.frame) >= 6 : #Failsafe condition, in the case of multiple packet arriving at once..
                reactor.callLater(0.5, self.dataReceived, b'')
            
            ########### RESPONSE_LOGIN
            if fieldsList[0][0] == 1 :          
                print('Received the login response...')
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
                print('Received the logout response...')
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
                print('Received the ping response...')
                lastServerEventID = fieldsList[1][0]
                if self.lastEventID != lastServerEventID :
                    print('Ping status : Not up-to-date, getting events required')
                    self.sendGetEventsRequestOIE(lastServerEventID - self.lastEventID)
                    
                else :
                    print('Ping status : up-to-date, preparing next ping')
                    reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE)
                    
            
                
            ########### RESPONSE_EVENTS        
            elif fieldsList[0][0] == 7 :
                print('Received the get_events response...')
                for i in range(len(fieldsList[1])):
                    if fieldsList[1][i][1] == 1 : #Message event
                        print('Message event received !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        user = self.store.getUserById(fieldsList[1][i][3])
                        print(user)
                        if user.userChatRoom == self.userRoomID and user.userId != self.userID:
                            self.clientProxy.chatMessageReceivedONE(user.userName, fieldsList[1][i][4])
                            print(fieldsList[1][i][4])
                        
                    elif fieldsList[1][i][1] == 2 : #New user event
                        print('A new user has been added !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        room = self.store.getMovieById(fieldsList[1][i][2])
                        self.store.addUser(fieldsList[1][i][4], fieldsList[1][i][3], room.movieId)
                        self.clientProxy.userUpdateReceivedONE(fieldsList[1][i][4], room.movieTitle)
                        moduleLogger.debug('GetEvents status : New user')
                        
                    elif fieldsList[1][i][1] == 3 : #Switch room event
                        print('A user switched room')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        name = self.store.getUserById(fieldsList[1][i][3]).userName
                        room = self.store.getMovieById(fieldsList[1][i][4]).movieTitle
                        self.store.updateUserChatroom(name, fieldsList[1][i][4])
                        self.clientProxy.userUpdateReceivedONE(name, room)
                        moduleLogger.debug('GetEvent status : User switched room')
                    
                    elif fieldsList[1][i][1] == 4 : #Logout event
                        print('A user disconnected !')
                        self.lastEventID = fieldsList[1][i][0]
                        
                        name = self.store.getUserById(fieldsList[1][i][3]).userName
                        self.store.removeUser(name)
                        self.clientProxy.userUpdateReceivedONE(name, ROOM_IDS.OUT_OF_THE_SYSTEM_ROOM)
                        moduleLogger.debug('GetEvent status : User logged out')
                        
                print('GetEvent status : up-to-date, preparing next ping')
                reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE)
                    
            
                    
            ########### RESPONSE_ROOMS
            elif fieldsList[0][0] == 9 :
                print('Received the get_room response...')
                #FieldsList returns the data in the following form : Room_id, IP, Port, Room_name, Nbr_users
                #AddMovie accepts it in the following form : Title, IP, Port, ID 
                moduleLogger.debug('Room status : Rooms list received')
                for i in range(len(fieldsList[1])):
                    if self.store.getMovieById(fieldsList[1][i][0]) is None :   
                        self.store.addMovie(fieldsList[1][i][3], fieldsList[1][i][1], fieldsList[1][i][2], fieldsList[1][i][0])
                
                c2wMovies = self.store.getMovieList() #get the movie list in the appropriate format
                movieList = []
                for i in range(len(c2wMovies)) :
                    if c2wMovies[i].movieTitle != ROOM_IDS.MAIN_ROOM :
                        movieList.append((c2wMovies[i].movieTitle, c2wMovies[i].movieIpAddress, c2wMovies[i].moviePort))
                c2wUsers = self.store.getUserList() #get the user list in the appropriate format
                print(c2wUsers)
                userList = []
                for i in range(len(c2wUsers)) :
                    userList.append((c2wUsers[i].userName, self.store.getMovieById(c2wUsers[i].userChatRoom).movieTitle))
                print(userList)
                self.clientProxy.initCompleteONE(userList, movieList) #send both to the UI
                print('Room status : UI has been updated')
                
                print('Room status : UI is ready, starting ping cycle')
                reactor.callLater(self.pingTimer, self.sendGetPingRequestOIE) #Then starts the Ping - Pong - GetEvents - ResponseEvents - Ping cycle
                    
                                   

            ########### RESPONSE_USERS
            elif fieldsList[0][0] == 11 :
                print('Received the get_user response...')
                #FieldsList returns the data in the following form : user_id, user_name, room_id
                #AddUser accepts it in the following form : Name, ID, Chatroom
                moduleLogger.debug('Users status : Users list received')
                for i in range(len(fieldsList[1])):
                    if not self.store.userExists(fieldsList[1][i][1]) :
                        self.store.addUser(fieldsList[1][i][1], fieldsList[1][i][0], fieldsList[1][i][2])
                        
                print('Users status : Users list fully updated, asking for rooms')
                self.sendGetRoomsRequestOIE(1, 255)
            
                
            ########### RESPONSE_SWITCH_ROOM
            elif fieldsList[0][0] == 13 :
                print('Received the switch room response...')
                if fieldsList[1][0] == 0 :
                    self.clientProxy.joinRoomOKONE()
                    self.userRoomID = self.futureRoomID
                    print('Switch room status : Done')
                elif fieldsList[1][0] == 1 :
                    print('Switch room status : Unknown error')
            
            
            ########### RESPONSE_NEW_MESSAGE
            elif fieldsList[0][0] == 15 :
                print('Received the put_new_message response')
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
