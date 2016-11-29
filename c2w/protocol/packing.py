# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

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

    message_type = 2;
    
    message_length = 0
   
    code = '!BHBH' 
    data = struct.pack(code,message_type,seq_number,user_id,message_length);
    return data 
    
###########
   
       
