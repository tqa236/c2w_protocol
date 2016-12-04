# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math
from . import misc

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
    last_event_id0 = int(last_event - last_event_id1*math.pow(2,16))
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
    
    message_type = 3
    message_length = 1
    
    code = '!BHBH' + 'B'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, status_code)
    return data

###########

def GET_PING(seq_number, user_id, last_event, room_id):
    
    message_type = 4
    message_length = 4
    
    last_event_id1 = last_event//65536
    last_event_id0 = last_event - last_event_id1*65536
    
    code = '!BHBH' + 'BHB'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1, last_event_id0, room_id)
    return data
    
###########

def RESPONSE_PING(last_event):
    message_type = 5
    message_length = 3
    
    last_event_id1 = last_event//65536
    last_event_id0 = last_event - last_event_id1*65536
    
    code = '!BHBH' + 'BH'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1, last_event_id0)
    return data

###########
 
def GET_EVENTS(seq_number, user_id, last_event, nbr_events, room_id):
    
    message_type = 6
    message_length = 5
    
    last_event_id1 = last_event//65536
    last_event_id0 = last_event - last_event_id1*65536
    
    code = '!BHBH' + 'BHBB'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, last_event_id1,last_event_id0, nbr_events, room_id)

    return data
    
###########

def CODE_EVENT(event_type, event_id,room_id,user_id, message) :

    event_id1 = event_id//65536
    event_id0 = event_id - event_id1*65536  
      
    if event_type == 0x01 :
        message_length = len(message)
        code = 'HB' + 'BBBH' +  str(message_length) + 's'
        
        data = struct.pack(code, event_id1, event_id0, event_type, room_id, user_id,message_length,message.encode('utf-8'))   
        
    elif event_type == 0x02 :
         message_length = len(message)
         code = 'HB' + 'BBBB' + str(message_length) + 's'
         data=struct.pack(code,event_id1, event_id0, event_type, room_id, user_id,message_length,message.encode('utf-8'))
       
    elif event_type == 0x03 :
         code = 'HB' + 'BBBB'
         data = struct.pack(code,event_id1, event_id0, event_type, message, user_id, room_id)
    
    elif event_type == 0x04 :
         code = 'HB' + 'BBB'
         data = struct.pack(code,event_id1, event_id0, event_type, room_id, user_id)
         
    return data
    
###########
    
def RESPONSE_EVENTS_HEAD(seq_number, user_id, nbr_events,message_length) :

    message_type = 0x07
    message_length = message_length + 1   
    
    code = 'BHBH' + 'B'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, nbr_events)
    return data
    
###########
    
def RESPONSE_EVENTS(seq_number, user_id, nbr_events, events_list) :
    # On organise les events de la façon suivante : Event_id, Event_type, room_id, user_id + les composantes particulières à chaque type dans l'ordre
    message_type = 7
    message_length = 1
    for i in range(len(events_list)) :
        message_length += len(events_list[i])
    
    code = 'BHBH' + 'B'
    data = struct.pack(code, message_type, seq_number, user_id, message_length, nbr_events)
    for i in range(len(events_list)) :
        event_id = events_list[i][0]
        event_id1 = math.floor(event/math.pow(2,16))
        event_id0 = last_event - event_id1*math.pow(2,16)
        code = 'BHBBB'
        if events_list[i][1] == 1 :
            code += 'H' + str(events_list[i][4]) + 's'
            data += struct.pack(code, events_list[i][0], events_list[i][1], events_list[i][2], events_list[i][3], events_list[i][4], events_list[i][5])
        elif events_list[i][1] == 2 :
            code += 'B' + str(events_list[i][4]) + 's'
            data += struct.pack(code, events_list[i][0], events_list[i][1], events_list[i][2], events_list[i][3], events_list[i][4], events_list[i][5])
        elif events_list[i][2] == 3 :
            code += 'B'
            data += struct.pack(code, events_list[i][0], events_list[i][1], events_list[i][2], events_list[i][3], events_list[i][4])
        else :
            data += struct.pack(code, events_list[i][0], events_list[i][1], events_list[i][2], events_list[i][3])
    
    return data
        
###########

def GET_ROOMS(seq_number,user_id,first_room_id,nbr_rooms):
    
    message_type = 8
    message_length = 2

    code = '!BHBH' + 'BB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,first_room_id,nbr_rooms)

    return data
    
###########

def RESPONSE_ROOMS(seq_number,user_id,rooms_list,n_users_room):

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
        room_id = rooms_list[i].movieID;
        ip_number = getListIP(rooms_list[i].movieIpAddress);
        port_number = rooms_list[i].moviePort;
        name = rooms_list[i].movieTitle;
        nbr_users = n_users_room[i];
        room_name_length = len(name);

        if i == 0:
            offset = 7;
        else:
            offset = offset + 9 + len(rooms_list[i-1].movieTitle);

        code = '!B'+'BBBB'+'HB'+ str(room_name_length) + 's' + 'B';
        struct.pack_into(code,data,offset,room_id,ip_number[0],ip_number[1],ip_number[2],ip_number[3],port_number,room_name_length,name.encode('utf-8'),nbr_users);

    return data;
    
###########

def GET_USERS(seq_number,user_id,first_user_id,nbr_users,room_id):
    
    message_type = 10
    message1_length = 3

    code = '!BHBH' + 'BBB'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,first_user_id,nbr_users,room_id)

    return data
    
###########

def RESPONSE_USERS(seq_number,user_id,users_list): 

    message_type = 0x0B;
    nbr_users = len(users_list);
    list_length = 0;

    for user in users_list:
        user_length = len(user.userName);
        list_length = list_length + 3 + user_length;

    message_length = list_length + 1;
    data = bytearray(6+message_length);    

    code = '!BHBH' + 'B';
    offset = 0;
    struct.pack_into(code,data,offset,message_type,seq_number,user_id,message_length,nbr_users);

    for i in range(nbr_users):
        user_id = users_list[i].userId;
        username = users_list[i].userName;
        room_id = users_list[i].userChatRoom;
        user_length = len(users_list[i].userName);

        if i == 0:
            offset = 7; 
        else:

            offset = offset + 3 + len(users_list[i-1].userName);        

        code = '!BB'+ str(user_length) + 's' + 'B';
        struct.pack_into(code,data,offset,user_id,user_length,username.encode('utf-8'),room_id);

    return data;
    
###########     
       
def PUT_SWITCH_ROOM(seq_number,user_id,room_id):
    
    message_type = 12
    message1_length = 1

    code = '!BHBH' + 'B'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id)

    return data
    
    
###########
    
def RESPONSE_SWITCH_ROOM(seq_number,user_id,status_code):

    message_type = 13
    message1_length = 1


    code = '!BHBH' + 'B'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,status_code)
    return data


###########     
       
def PUT_NEW_MESSAGE(seq_number,user_id,room_id,message):
    
    message_type = 14
    message2_length = len(message)
    message1_length = 3 + message2_length

    code = '!BHBH' + 'BH' + str(message2_length) + 's'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,room_id,message2_length,message.encode('utf-8'))

    return data


###########  
  
def RESPONSE_NEW_MESSAGE(seq_number,user_id,status_code):
    
    message_type = 0x0F
    message1_length = 1


    code = '!BHBH' + 'B'
    data = struct.pack(code,message_type,seq_number,user_id,message1_length,status_code)

    return data


###########

   
       
