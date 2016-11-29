# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math 

###########     
   
def PUT_LOGIN(seq_number,username):

    message_type = 0x00
    user_id = 0
    message_length = 1 + len(username)
    UL = len(username)
    code = '!BHBH' + 'B' + str(UL) + 's'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,UL,username.encode('utf-8'))
    return data

###########     
       
def PUT_NEW_MESSAGE(seq_number,user_id,room_id,message):
    
    message_type = 0x0E;
    message2_length = len(message);
    message1_length = 3 + message2_length;


    code = '!BHBH' + 'BH' + str(message2_length) + 's';

    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id,message2_length,message.encode('utf-8'));

    return data;

###########     
       
def PUT_SWITCH_ROOM(seq_number,user_id,room_id):
    
    message_type = 0x0C;
    message1_length = 1;


    code = '!BHBH' + 'B';

    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id);

    return data;
    
###########

def PUT_LOGOUT(seq_number,user_ID):

    message_type = 0x02;
    
    message_length = 0
   
    code = '!BHBH' 
    data = struct.pack(code,message_type,seq_number,user_id,message_length);
    return data 
    
###########

def GET_PING(seq_number,user_id,last_event_id,room_id):
    
    message_type = 0x04
    message_length = 4
    
    last_event_id_temp = math.floor(last_event_id/256);
    last_event_id0 = last_event_id - 256*last_event_id_temp;
    last_event_id2 = math.floor(last_event_id_temp/256);
    last_event_id1 = last_event_id_temp - 256*last_event_id2;
    
    code = '!BHBH' + 'BBBB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id2,last_event_id1,last_event_id0,room_id)
    return data
     
###########
 
def GET_EVENTS(seq_number,user_id,last_event_id,nbr_events,room_id):
    
    message_type = 0x06
    message_length = 5
    
    last_event_id_temp = math.floor(last_event_id/256);
    last_event_id0 = last_event_id - 256*last_event_id_temp;
    last_event_id2 = math.floor(last_event_id_temp/256);
    last_event_id1 = last_event_id_temp - 256*last_event_id2;
    
    code = '!BHBH' + 'BBBBB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id2,last_event_id1,last_event_id0,nbr_events,room_id)

    return data
    
###########


    
###########
   

   
       
