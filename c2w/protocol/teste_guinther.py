# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from client_model import c2wClientModel
import struct
import time
import math

#from . import c2w.main.client_model 

########### TESTE GET_PING 

def GET_PING(seq_number, user_id, last_event, room_id):
    
    message_type = 4
    message_length = 4
    
    last_event_id1 = last_event//65536
    last_event_id0 = last_event - last_event_id1*65536
    
    code = '!BHBH' + 'BHB'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1, last_event_id0, room_id)
    return data

###########
datagram = GET_PING(48,8,88888,15)
###########

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)
if messageHeader[0] == 4 : #Ping request dataType
    messageBody = struct.unpack('!BHB', datagram[6:])
    lastEventID = int(messageBody[0]*math.pow(2,16) + messageBody[1])
    fieldsList.append([lastEventID, messageBody[2]])
    
print(fieldsList)

########### TESTE GET_EVENTS
""" 
def GET_EVENTS(seq_number,user_id,last_event_id,nbr_events,room_id):
    
    message_type = 0x06
    message_length = 5
    
    last_event_id_temp = math.floor(last_event_id/256);
    last_event_id0 = last_event_id - 256*last_event_id_temp;
    last_event_id2 = math.floor(last_event_id_temp/256);
    last_event_id1 = last_event_id_temp - 256*last_event_id2;
    
    print(str(last_event_id2))   
    print(str(last_event_id1))  
    print(str(last_event_id0))
       
    code = '!BHBH' + 'BBBBB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id2,last_event_id1,last_event_id0,nbr_events,room_id)
    
    print(str(data))
        
    return data
    
###########
datagram = GET_EVENTS(48,8,88888,255,15)
###########

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)

#GET_EVENTS
if messageHeader[0] == 6 : #Events data request dataType
    messageBody = struct.unpack('!BHBB', datagram[6:])
    lastEventID = int(messageBody[0]*math.pow(2,16) + messageBody[1])
    fieldsList.append([lastEventID, messageBody[2], messageBody[3]])

print(fieldsList)    
"""

########### TESTE GET_ROOMS
"""
def GET_ROOMS(seq_number,user_id,first_room_id,nbr_rooms):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x08;
    message_length = 0x02;


    code = '!BHBH' + 'BB';

    data = struct.pack(code,message_type,seq_number,user_id,message_length,first_room_id,nbr_rooms);

    return data;
    
###########
datagram = GET_ROOMS(5,16,3,4);
###########

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)

if messageHeader[0] == 8 : #Rooms data request
    messageBody = struct.unpack('!BB', datagram[6:])
    fieldsList.append([messageBody[0], messageBody[1]])
    
print(fieldsList)
"""
    
########### TESTE GET_USERS
"""
def GET_USERS(seq_number,user_id,first_user_id,nbr_users,room_id):
    
    message_type = 0x0A;
    message1_length = 3;

    code = '!BHBH' + 'BBB';

    data = struct.pack(code,message_type,seq_number,user_id,message1_length,first_user_id,nbr_users,room_id);

    return data;
    
###########
datagram = GET_USERS(1,2,3,4,5);
###########

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)

if messageHeader[0] == 10 : #Users data request
    messageBody = struct.unpack('!BBB', datagram[6:])
    fieldsList.append([messageBody[0], messageBody[1], messageBody[2]])
    
print(fieldsList)    
"""
########### RESPONSE_ROOMS
"""
def decodeRooms(entryNumber, datagram):
"""
   #:param byte: the list part of the datagram to decode
    
   # Called by decode to take care of the list part of Room response packet
"""
    #This function should :
    # - Unpack a Rooms response datagram
    
    resultList = []
    for i in range(entryNumber) : #Room (room_id, IP, Port, name_length, room_name, nbr_users)
        information = struct.unpack('!BBBBBHB', datagram[:8])
        room_content = struct.unpack('!'+str(information[6])+'s'+'B',datagram[8:9+information[6]]) #Moi(Güinther), j'ai ajouté +'s'
        resultList.append([information[0], (information[1], information[2], information[3], information[4]), information[5], room_content[0].decode('utf-8'), room_content[1]]) #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users
        datagram = datagram[(9+information[6]):]
    return resultList;

def RESPONSE_ROOMS(seq_number,user_id,rooms_list):
    
    message_type = 0x09;
    nbr_rooms = len(rooms_list);

    list_length = 0;

    for rooms in rooms_list:
        room_length = len(rooms.movieTitle);
        list_length = list_length + 9 + room_length;
    
    message_length = list_length + 1;  
    data = bytearray(6+message_length);
    
    code = '!BHBH' + 'B';
    offset = 0;
    struct.pack_into(code,data,offset,message_type,seq_number,user_id,message_length,nbr_rooms);

    for i in range(nbr_rooms):
        room_id = rooms_list[i].movieId;
        ip_number = rooms_list[i].movieIpAddress;
        port_number = rooms_list[i].moviePort;
        name = rooms_list[i].movieTitle;
        nbr_users = rooms_list[i].nbr_users;

        room_name_length = len(rooms_list[i].movieTitle);
        
        if i == 0:
            offset = 7; 
        else:
            offset = offset + 9 + len(rooms_list[i-1].movieTitle);
        
        code = '!B'+'BBBB'+'HB'+ str(room_name_length) + 's' + 'B';
        struct.pack_into(code,data,offset,room_id,ip_number[0],ip_number[1],ip_number[2],ip_number[3],port_number,room_name_length,name.encode('utf-8'),nbr_users);

    return data;

###########
store = c2wClientModel();

store.addMovie('movieTitle1', [189,22,56,0], 8888, 12, 15);
store.addMovie('movieTitle2', [189,22,56,1], 8887, 11, 14);
store.addMovie('movieTitle3', [189,22,56,2], 8886, 10, 13);

liste = store.getMovieList(); 

datagram = RESPONSE_ROOMS(5,15, liste);
###########


#This function returns the fieldsList list
#fieldsList[0] contains the Header, in particular fieldsList[0][0] contain the messageType
#fieldsList[1] contains the content of message_data, in the format described by messageType (note that length fields have been removed)

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)


#RESPONSE_ROOMS
if messageHeader[0] == 9 : #Rooms data response
    nbrRooms = struct.unpack('!B', datagram[6:7])[0]
    fieldsList.append(decodeRooms(nbrRooms, datagram[7:]))
    
"""    

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
