# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math 

########### TESTE GET_PING 
"""
def GET_PING(seq_number,user_id,last_event_id,room_id):
    

    message_type = 0x04
    message_length = 4
    
    last_event_id_temp = math.floor(last_event_id/256);
    last_event_id0 = last_event_id - 256*last_event_id_temp;
    last_event_id2 = math.floor(last_event_id_temp/256);
    last_event_id1 = last_event_id_temp - 256*last_event_id2;
    

    print(str(last_event_id2))   
    print(str(last_event_id1))  
    print(str(last_event_id0))
          
    code = '!BHBH' + 'BBBB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id2,last_event_id1,last_event_id0,room_id)
    print(str(data))
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
"""

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

     
