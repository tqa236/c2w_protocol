+# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
import time 

def PUT_LOGIN(userName):
    l = str(len(userName))
    code = '!BHBH'+'B' + str(len(userName)) + 's'
    data = struct.pack(code,l,userName.encode('utf-8'))
    print(data)
    return data
