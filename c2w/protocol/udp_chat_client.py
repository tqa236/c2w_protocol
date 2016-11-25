# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
import struct
import math

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
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

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

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
        pass

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
        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        pass

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
        fieldsList = udp_chat_client.decode(datagram)
        
    def decode(self, datagram):
        """
        :param byte: the payload of the UDP packet to decode
        
        Called by datagramReceived.
        """
        #This function should :
        # - Unpack the datagram
        
        #This function returns the fieldsList list
        #fieldsList[0] contains the Header, in particular fieldsList[0][0] contain the messageType
        #fieldsList[1] contains the content of message_data, in the format described by messageType (note that length fields have been removed)
        
        fieldsList = []
        messageHeader = struct.unpack('!BHBH', datagram[:6])
        fieldsList.append(messageHeader)
        if messageHeader[0] == 0 : #Login request dataType
            UL = struct.unpack('!B', datagram[6:8])
            Username = struct.unpack('!' + str(UL) + 's', datagram[8:])
            fieldsList.append(Username)
        elif messageHeader[0] == 1 : #Login response dataType
            messageBody = struct.unpack('!BBBH', datagram[6:]) #Struct does not have a 3 byte type, so we use a '!BH' type instead
            fieldsList += messageBody[:2]
            lastEventID = messageBody[2]*math.pow(2,16) + messageBody[3] #For the BH type to be converted into a 3 byte value we need to multiply the single byte type (B) by 2^16
            fieldsList.append([messageBody[0], messageBody[1], lastEventID])
        elif messageHeader[0] == 2 : #Logout request dataType
            fieldsList.append([])
        elif messageHeader[0] == 3 : #Logout response dataType
            messageBody = struct.unpack('!B', datagram[6:])
            fieldsList.append([messageBody[0]])
        elif messageHeader[0] == 4 : #Ping request dataType
            messageBody = struct.unpack('!BHB', datagram[6:])
            lastEventID = messageBody[0]*math.pow(2,16) + messageBody[1]
            fieldsList.append([lastEventID, messageBody[2]])
        elif messageHeader[0] == 5 : #Ping response dataType
            messageBody = struct.unpack('!BH', datagram[6:])
            lastEventID = messageBody[0]*math.pow(2,16) + messageBody[1]
            fieldsList.append([lastEventID])
        elif messageHeader[0] == 6 : #Events data request dataType
            messageBody = struct.unpack('!BHBB', datagram[6:])
            lastEventID = messageBody[0]*math.pow(2,16) + messageBody[1]
            fieldsList.append([lastEventID, messageBody[2], messageBody[3]])
        elif messageHeader[0] == 7 : #Events data response dataType
            nbrEvents = struct.unpack('!B', datagram[6:8])
            fieldsList.append(udp_chat_client.decodeEvents(nbreEvents, datagram[8:]))
        elif messageHeader[0] == 8 : #Rooms data request
            messageBody = struct.unpack('!BB', datagram[6:])
            fieldsList.append([messageBody[0], messageBody[1]])
        elif messageHeader[0] == 9 : #Rooms data response
            nbrRooms = struct.unpack('!B', datagram[6:8])
            fieldsList.append(udp_chat_client.decodeRooms(nbreRooms, datagram[8:]))
        elif messageHeader[0] == 10 : #Users data request
            messageBody = struct.unpack('!BBB', datagram[6:])
            fieldsList.append([messageBody[0], messageBody[1], messageBody[2]])
        elif messageHeader[0] == 11 : #Users reponse request
            nbrUsers = struct.unpack('!B', datagram[6:8])
            fieldsList.append(udp_chat_client.decodeUsers(nbreUsers, datagram[8:]))
        elif messageHeader[0] == 12 : #Switch room request
            messageBody = struct.unpack('!B', datagram[6:])
            fieldsList.append([messageBody[0]])
        elif messageHeader[0] == 13 : #Switch room response 
            messageBody = struct.unpack('!B', datagram[6:])
            fieldsList.append([messageBody[0]])
        elif messageHeader[0] == 14 : #New message request
            messageBody = struct.unpack('!BH', datagram[6:10])
            messageBody += struct.unpack('!'+str(messageBody[1])+'s', datagram[10:])
            fieldsList.append([messageBody[0], messageBody[2]])
        elif messageHeader[0] == 15 : #New_message response
            messageBody = struct.unpack('!B', datagram[6:])
            fieldsList.append([messageBody[0]])
        return fieldsList
        
    def decodeUsers(self, entryNumber, datagram):
        """
        :param byte: the list part of the datagram to decode
        
        Called by decode to take care of the list part of User response packet
        """
        #This function should :
        # - Unpack a User reponse datagram
        
        resultList = []
        for i in range(entryNumber) : #User (user_id, name_length, user_name, room_id)
            information = struct.unpack('!BB', datagram[:2])
            user_content = struct.unpack('!'+str(information[1])+'B')
            resultList.append([information[0], user_content[0], user_content[1]]) #Returned in the following form : user_id, user_name, room_id
            datagram = datagram[(3+information[1]):]
        return resultList



    def decodeRooms(self, entryNumber, datagram):
        """
        :param byte: the list part of the datagram to decode
        
        Called by decode to take care of the list part of Room response packet
        """
        #This function should :
        # - Unpack a Rooms response datagram
        
        resultList = []
        for i in range(entryNumber) : #Room (room_id, IP, Port, name_length, room_name, nbr_users)
            information = struct.unpack('!BIHB', datagram[:8])
            room_content = struct.unpack('!'+str(information[3])+'B')
            resultList.append([information[0], information[1], information[2], room_content[0], room_content[1]]) #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users
            datagram = datagram[(9+information[3]):]
        return resultList



    def decodeEvents(self, entryNumber, datagram):
        """
        :param byte: the list part of the datagram to decode
        
        Called by decode to take care of the list part of Events response packet
        """
        #This function should :
        # - Unpack a Events response datagram
        
        resultList = []
        for i in range(entryNumber) :
            eventHeader = struct.unpack('!BHB', datagram[:4])
            eventId = eventHeader[0]*math.pow(2,16) + eventHeader[1]
            eventType = eventHeader[2]
            if eventType == 1 : #Message event (room_id, user_id, message_length, message)
                information = struct.unpack('!BBH', datagram[4:8])
                message = struct.unpack('!'+str(information[2])+'s',datagram[8:])
                resultList.append([eventId, eventType, information[0], information[1], message]) #Returned in the following form : EventID, Type, Room, User, Message
                datagram = datagram[(8+information[2]):]
            if eventType == 2 : #New user event(room_id, user_id, username_length, username)
                information = struct.unpack('!BBB', datagram[4:7])
                message = struct.unpack('!'+str(information[2])+'s',datagram[7:])
                resultList.append([eventId, eventType, information[0], information[1], message]) #Returned in the following form : EventID, Type, Room, User, Username
                datagram = datagram[(7+information[2]):]
            if eventType == 3 : #Switch room event(room_id, user_id, new_room_id)
                information = struct.unpack('!BBB', datagram[4:7])
                resultList.append([eventId, eventType, information[0], information[1], information[2]]) #Returned in the following form : EventID, Type, Room, User, NEWRoom
                datagram = datagram[7:]
            if eventType == 4 : #Logout event(room_id, user_id)
                information = struct.unpack('!BB', datagram[4:6])
                resultList.append([eventId, eventType, information[0], information[1]]) #Returned in the following form : EventID, Type, Room, User
                datagram = datagram[6:]
        return resultList    
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
