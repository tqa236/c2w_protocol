# -*- coding: utf-8 -*-
import struct
import math


def decode(datagram):
    

    #This function returns the fieldsList list
    #fieldsList[0] contains the Header, in particular fieldsList[0][0] contain the messageType
    #fieldsList[1] contains the content of message_data, in the format described by messageType (note that length fields have been removed)
    
    fieldsList = []
    messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
    fieldsList.append(messageHeader)
    if messageHeader[0] == 0 : #Login request dataType
        UL = struct.unpack('!B', datagram[6:7])
        Username = struct.unpack('!' + str(UL) + 's', datagram[7:])
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
        nbrEvents = struct.unpack('!B', datagram[6:7])
        fieldsList.append(unpacking.decodeEvents(nbreEvents, datagram[7:]))
    elif messageHeader[0] == 8 : #Rooms data request
        messageBody = struct.unpack('!BB', datagram[6:])
        fieldsList.append([messageBody[0], messageBody[1]])
    elif messageHeader[0] == 9 : #Rooms data response
        nbrRooms = struct.unpack('!B', datagram[6:7])
        fieldsList.append(unpacking.decodeRooms(nbreRooms, datagram[7:]))
    elif messageHeader[0] == 10 : #Users data request
        messageBody = struct.unpack('!BBB', datagram[6:])
        fieldsList.append([messageBody[0], messageBody[1], messageBody[2]])
    elif messageHeader[0] == 11 : #Users reponse request
        nbrUsers = struct.unpack('!B', datagram[6:7])
        fieldsList.append(unpacking.decodeUsers(nbreUsers, datagram[7:]))
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
        user_content = struct.unpack('!'+str(information[1])+'B')
        resultList.append([information[0], user_content[0], user_content[1]]) #Returned in the following form : user_id, user_name, room_id
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
        room_content = struct.unpack('!'+str(information[6])+'s'+'B') #Moi(Güinther), j'ai ajouté +'s'
        resultList.append([information[0], (information[1], information[2], information[3], information[4]), information[5], room_content[0], room_content[1]]) #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users
        datagram = datagram[(9+information[3]):]
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
