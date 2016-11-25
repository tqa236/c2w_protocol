# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def GET_PING(seq_number,user_ID,last_event_id1,last_event_id2,room_id):
    

    message_type = 4
    message_length = 4
    code = '!BHBH' + 'BHB'
    data = struct.pack(code,message_type,seq_number,user_id,message_length,last_event_id1,last_event_id2,room_id)
    return data
