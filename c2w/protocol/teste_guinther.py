# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time
import math 

########### 

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

     
