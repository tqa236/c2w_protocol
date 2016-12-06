# -*- coding: utf-8 -*-
import struct
import math
from . import misc


def decode(datagram):
    

    #This function returns the fieldsList list
    #fieldsList[0] contains the Header, in particular fieldsList[0][0] contain the messageType
    #fieldsList[1] contains the content of message_data, in the format described by messageType (note that length fields have been removed)
    
    fieldsList = []
    messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
    fieldsList.append(messageHeader)
    
    #PUT_LOGIN
    if messageHeader[0] == 0 :
        UL = struct.unpack('!B', datagram[6:7])
        Username = struct.unpack('!' + str(UL[0]) + 's', datagram[7:])
        fieldsList.append([Username[0].decode('utf-8')])
    
    #RESPONSE_LOGIN    
    elif messageHeader[0] == 1 :
        messageBody = struct.unpack('!BBBH', datagram[6:]) #Struct does not have a 3 byte type, so we use a '!BH' type instead
        lastEventID = int(messageBody[2]*65536 + messageBody[3]) #For the BH type to be converted into a 3 byte value we need to multiply the single byte type (B) by 2^16
        fieldsList.append([messageBody[0], messageBody[1], lastEventID])
    
    #PUT_LOGOUT
    elif messageHeader[0] == 2 :
        fieldsList.append([])
    
    #RESPONSE_LOGOUT
    elif messageHeader[0] == 3 :
        messageBody = struct.unpack('!B', datagram[6:])
        fieldsList.append([messageBody[0]])
    
    #GET_PING
    elif messageHeader[0] == 4 :
        messageBody = struct.unpack('!BHB', datagram[6:])
        lastEventID = messageBody[0]*65536 + messageBody[1]
        fieldsList.append([lastEventID, messageBody[2]])
    
    #RESPONSE_PING
    elif messageHeader[0] == 5 :
        messageBody = struct.unpack('!BH', datagram[6:])
        lastEventID = messageBody[0]*65536 + messageBody[1]
        fieldsList.append([lastEventID])
    
    #GET_EVENTS
    elif messageHeader[0] == 6 :
        messageBody = struct.unpack('!BHBB', datagram[6:])
        lastEventID = int(messageBody[0]*math.pow(2,16) + messageBody[1])
        fieldsList.append([lastEventID, messageBody[2], messageBody[3]])
    
    #RESPONSE_EVENTS
    elif messageHeader[0] == 7 :
        nbrEvents = struct.unpack('!B', datagram[6:7])
        fieldsList.append(decodeEvents(nbrEvents[0], datagram[7:]))
    
    #GET_ROOMS
    elif messageHeader[0] == 8 :
        messageBody = struct.unpack('!BB', datagram[6:])
        fieldsList.append([messageBody[0], messageBody[1]])
    
    #RESPONSE_ROOMS
    elif messageHeader[0] == 9 :
        nbrRooms = struct.unpack('!B', datagram[6:7])
        fieldsList.append(decodeRooms(nbrRooms[0], datagram[7:]))
    
    #GET_USERS
    elif messageHeader[0] == 10 :
        messageBody = struct.unpack('!BBB', datagram[6:])
        fieldsList.append([messageBody[0], messageBody[1], messageBody[2]])
    
    #RESPONSE_USERS
    elif messageHeader[0] == 11 :
        nbrUsers = struct.unpack('!B', datagram[6:7])
        fieldsList.append(decodeUsers(nbrUsers[0], datagram[7:]))
    
    #PUT_SWITCH_ROOM
    elif messageHeader[0] == 12 :
        messageBody = struct.unpack('!B', datagram[6:])
        fieldsList.append([messageBody[0]])
    
    #RESPONSE_SWITCH_ROOM
    elif messageHeader[0] == 13 :
        messageBody = struct.unpack('!B', datagram[6:])
        fieldsList.append([messageBody[0]])
    
    #PUT_NEW_MESSAGE
    elif messageHeader[0] == 14 :
        messageBody = struct.unpack('!BH', datagram[6:9])
        messageBody += struct.unpack('!'+str(messageBody[1])+'s', datagram[9:])
        fieldsList.append([messageBody[0], messageBody[2].decode('utf-8')])
    
    #RESPONSE_NEW_MESSAGE
    elif messageHeader[0] == 15 :
        messageBody = struct.unpack('!B', datagram[6:])
        fieldsList.append([messageBody[0]])
        
    return fieldsList
    
def decodeUsers(entryNumber, datagram):
    """
    :param byte: the list part of the datagram to decode
    
    Called by decode to take care of the list part of User response packet
    """
    #This function should :
    # - Unpack a User reponse datagram
    
    resultList = []
    for i in range(entryNumber) : #User (user_id, name_length, user_name, room_id)
        information = struct.unpack('!BB', datagram[:2])
        user_content = struct.unpack('!'+str(information[1])+'s'+'B', datagram[2:2+information[1]+1])
        resultList.append([information[0], user_content[0].decode('utf-8'), user_content[1]]) #Returned in the following form : user_id, user_name, room_id
        datagram = datagram[(3+information[1]):]
    return resultList



def decodeRooms(entryNumber, datagram):
    """
    :param byte: the list part of the datagram to decode
    
    Called by decode to take care of the list part of Room response packet
    """
    #This function should :
    # - Unpack a Rooms response datagram
    
    resultList = []
    for i in range(entryNumber) : #Room (room_id, IP, Port, name_length, room_name, nbr_users)
        information = struct.unpack('!BBBBBHB', datagram[:8])
        ipAdress = misc.decodeIpAdress(information[1], information[2], information[3], information[4])
        room_content = struct.unpack('!'+str(information[6])+'sB',datagram[8:8 + information[6] + 1])
        resultList.append([information[0], ipAdress, information[5], room_content[0].decode('utf-8'), room_content[1]]) #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users
        datagram = datagram[(9+information[6]):]
    return resultList;

def decodeEvents(entryNumber, datagram):
    """
    :param byte: the list part of the datagram to decode
    
    Called by decode to take care of the list part of Events response packet
    """
    #This function should :
    # - Unpack a Events response datagram
    
    resultList = []
    for i in range(entryNumber) :
        eventHeader = struct.unpack('!BHB', datagram[:4])
        eventId = eventHeader[0]*65536 + eventHeader[1]
        eventType = eventHeader[2]
        if eventType == 1 : #Message event (room_id, user_id, message_length, message)
            information = struct.unpack('!BBH', datagram[4:8])
            message = struct.unpack('!'+str(information[2])+'s',datagram[8:8+information[2]])
            resultList.append([eventId, eventType, information[0], information[1], message[0].decode('utf-8')]) #Returned in the following form : EventID, Type, Room, User, Message
            datagram = datagram[(8+information[2]):]
        if eventType == 2 : #New user event(room_id, user_id, username_length, username)
            information = struct.unpack('!BBB', datagram[4:7])
            message = struct.unpack('!'+str(information[2])+'s',datagram[7:7+information[2]])
            resultList.append([eventId, eventType, information[0], information[1], message[0].decode('utf-8')]) #Returned in the following form : EventID, Type, Room, User, Username
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
