# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging

import c2w
from c2w.main.lossy_transport import LossyTransport
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')
from c2w.main.constants import ROOM_IDS
import time
import c2w.main.constants

from . import unpacking
from . import packing
import struct
import math
from . import misc
from twisted.internet import reactor
from c2w.main.client_model import c2wClientModel
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_client_protocol')


class c2wTcpChatClientProtocol(Protocol):

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
        self.clientProxy = clientProxy
        self.buffer = bytearray(0) # Only save the incomplete part of a message
        self.userID = 0 #This vatiable contains the id of the client that was set by the server (initially set to 0)
        self.lastEventID = 0 #This variable contains the id of the last event the client is currently aware of.
        self.seq_number = 0 #This variable contains the sequence number used to track packet loss
        self.userRoomID = 0 #This variable contains the room the client is currently in.
        self.entry_number_awaited = 0 #This variable contains the number of entry the client is expecting from the next multi-entry response
        self.store = c2wClientModel() #The c2wClientModel is a class used to store all data about users and movies

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        moduleLogger.debug('loginRequest called with username=%s', userName)
        packet = packing.PUT_LOGIN(self.seq_number,userName)
        print(packet)
        self.transport.write(packet)   

    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        pass

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
        self.transport.write(packet)

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
        self.transport.write(packet)


########### GET_ROOMS   
    #OK
    def sendGetRoomsRequestOIE(self,first_room_id, nbr_rooms):
        """
        This fuction is used by the chatClientProtocol to get a list of current rooms
        """
        
        moduleLogger.debug('Get rooms request called')
        print('hahaha = ',self.seq_number)
        self.entry_number_awaited = nbr_rooms
        packet = packing.GET_ROOMS(self.seq_number, self.userID, first_room_id, nbr_rooms)      
        self.transport.write(packet)



    def sendGetUsersRequestOIE(self,first_user_id, nbr_users):
        """
        This function is used by the chatClientProtocol to get a list of current users
        """
        
        moduleLogger.debug('Get users request called')
        
        packet = packing.GET_USERS(self.seq_number, self.userID, first_user_id, nbr_users, self.userRoomID)      
        self.transport.write(packet)

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """
        self.buffer = self.buffer + data
        if len(self.buffer) >= 6:
            header = self.buffer[:6]
            messageInfo = struct.unpack('!BHBH',header)
            messageLength = messageInfo[3] + 6
            if messageLength <= len(self.buffer):
                datagram = self.buffer[:messageLength] # the entire message
                fieldsList = unpacking.decode(datagram)
                print(fieldsList)
                self.buffer = self.buffer[messageLength:] # the rest of the message
                
                if fieldsList[0][0] == 1 :          
                    if fieldsList[1][0] == 0 :                    
                        moduleLogger.debug('Login status : Done')
                        self.userID = fieldsList[1][1]
                        self.lastEventID = fieldsList[1][2]
                        self.sendGetUsersRequestOIE(1, 255)
                    elif fieldsList[1][0] == 1 :
                        self.clientProxy.connectionRejectedONE('Unknow error')
                        moduleLogger.debug('Login status : Unknown error')
                    elif fieldsList[1][0] == 2 :
                        self.clientProxy.connectionRejectedONE('Too many users')
                        moduleLogger.debug('Login status : Too many users')
                    elif fieldsList[1][0] == 3 :
                        self.clientProxy.connectionRejectedONE('Invalid username')
                        moduleLogger.debug('Login status : Invalid username')
                    elif fieldsList[1][0] == 4 :
                        self.clientProxy.connectionRejectedONE('Username not available')
                        moduleLogger.debug('Login status : Username not available')

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
                            self.store.addMovie(fieldsList[1][i][3], fieldsList[1][i][1], fieldsList[1][i][2], fieldsList[1][i][0])
                    
                    if n < self.entry_number_awaited and n !=0 :
                        print('Room status : Asking for more rooms')
                        self.sendGetRoomsRequestOIE(n, self.entry_number_awaited - n)
                        
                    else : 
                        c2wMovies = self.store.getMovieList() #get the movie list in the appropriate format
                        movieList = []
                        for i in range(len(c2wMovies)) :
                            if c2wMovies[i].movieTitle != ROOM_IDS.MAIN_ROOM :
                                movieList.append((c2wMovies[i].movieTitle, c2wMovies[i].movieIpAddress, c2wMovies[i].moviePort))
                        print(movieList)
                        c2wUsers = self.store.getUserList() #get the user list in the appropriate format
                        userList = []
                        for i in range(len(userList)) :
                            userList.append((c2wUsers[i].userName, self.store.getMovieByID(c2wUsers[i].userChatRoom).movieTitle))
                        self.clientProxy.initCompleteONE(userList, movieList) #send both to the UI
                        print('Room status : UI has been updated')
                        
                        print('Room status : UI is ready, starting ping cycle')
                        self.sendGetPingRequestOIE() #Then starts the Ping - Pong - GetEvents - ResponseEvents - Ping cycle
                    
                                   


                ########### RESPONSE_USERS
                elif fieldsList[0][0] == 11 :
                    n = 0
                    #FieldsList returns the data in the following form : user_id, user_name, room_id
                    #AddUser accepts it in the following form : Name, ID, Chatroom
                    moduleLogger.debug('Users status : Users list received')
                    for i in range(1, len(fieldsList[1])):
                        n += 1
                        if self.store.getUserById(fieldsList[1][i][0]) == None :
                            self.store.addUser(fieldsList[1][i][1], fieldsList[1][i][0], fieldsList[1][i][2])
                            
                    if n < self.entry_number_awaited and n !=0 :
                        moduleLogger.debug('Users status : Asking for more users')
                        self.sendGetRoomsRequestOIE(n, self.entry_number_awaited - n)
                    else :
                        moduleLogger.debug('Users status : Users list fully updated, asking for rooms')
                        self.sendGetRoomsRequestOIE(1, 255)                        



                    
