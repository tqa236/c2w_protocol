# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math 

###########     
   
def PUT_LOGIN(seq_number, username):

    message_type = 0
    user_id = 0
    UL = len(username)
    message_length = 1 + UL
    
    code = '!BHBH' + 'B' + str(UL) + 's'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, UL, username.encode('utf-8'))
    return data


###########

def RESPONSE_LOGIN(seq_number, user_id, username, last_event, status_code):
    message_type = 1
    server_id = 0
    message_length = 5
    last_event_id1 = math.floor(last_event/math.pow(2,16))
    last_event_id0 = last_event - last_event_id0*math.pow(2,16)
    
    code = '!BHBH' + 'BBBH'
    data = struct.pack(code, message_type, seq_number, server_id, message_length, status_code, user_id, last_event_id1, last_event_id0)
    return data

###########

def PUT_LOGOUT(seq_number, user_id):

    message_type = 2    
    message_length = 0
   
    code = '!BHBH' 
    data = struct.pack(code, message_type, seq_number, user_id, message_length)
    return data 

###########

def RESPONSE_LOGOUT(seq_number, user_id, status_code):
    
    message_type = 3;
    message_length = 1
    
    code = '!BHBH' + 'B'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, status_code);
    return data

###########

def GET_PING(seq_number, user_id, last_event_id, room_id):
    
    message_type = 4
    message_length = 4
    
    last_event_id1 = math.floor(last_event/math.pow(2,16))
    last_event_id0 = last_event - last_event_id0*math.pow(2,16)
    
    code = '!BHBH' + 'BHB'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1, last_event_id0, room_id)
    return data
    
###########

def RESPONSE_PING(last_event):
    message_type = 5
    message_length = 3
    
    last_event_id1 = math.floor(last_event/math.pow(2,16))
    last_event_id0 = last_event - last_event_id0*math.pow(2,16)
    
    code = '!BHBH' + 'BH'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1, last_event_id0)
    return data

###########
 
def GET_EVENTS(seq_number, user_id, last_event_id, nbr_events, room_id):
    
    message_type = 6
    message_length = 5
    
    last_event_id1 = math.floor(last_event/math.pow(2,16))
    last_event_id0 = last_event - last_event_id0*math.pow(2,16)
    
    code = '!BHBH' + 'BHBB'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1,last_event_id0, nbr_events, room_id)

    return data
    
###########
    
def RESPONSE_EVENTS(nbr_events, events_list) :
    return None
    

###########

def GET_ROOMS(seq_number,user_id,first_room_id,nbr_rooms):
    
    message_type = 8
    message_length = 2

    code = '!BHBH' + 'BB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,first_room_id,nbr_rooms)

    return data
    
###########
    
def RESPONSE_ROOMS(nbr_rooms, rooms_list) :
    return None
    
###########

def GET_USERS(seq_number,user_id,first_user_id,nbr_users,room_id):
    
    message_type = 10
    message1_length = 3

    code = '!BHBH' + 'BBB'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,first_user_id,nbr_users,room_id)

    return data

###########
    
def RESPONSE_USERS(nbr_users, users_list) :
    return None
    
    
###########     
       
def PUT_SWITCH_ROOM(seq_number,user_id,room_id):
    
    message_type = 12
    message1_length = 1

    code = '!BHBH' + 'B'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id);

    return data;
    
    
###########
    
def RESPONSE_SWITCH_ROOM(seq_number,user_id,status_code):

    message_type = 13;
    message1_length = 1;


    code = '!BHBH' + 'B';
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,status_code);
    return data;


###########     
       
def PUT_NEW_MESSAGE(seq_number,user_id,room_id,message):
    
    message_type = 14
    message2_length = len(message);
    message1_length = 3 + message2_length

    code = '!BHBH' + 'BH' + str(message2_length) + 's'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id,message2_length,message.encode('utf-8'))

    return data;


###########  
  
def RESPONSE_NEW_MESSAGE(seq_number,user_id,status_code):
    
    message_type = 0x0F;
    message1_length = 1;


    code = '!BHBH' + 'B;
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,status_code);

    return data;


###########

   
       
