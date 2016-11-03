import struct

# sibylPackage module

def preparePack(time, data) :
    return struct.pack('IH'+str(len(data))+'s', time, len(data) + 6, data.encode('utf-8'))

def unpackDatagram(datagram) :
    return struct.unpack('IH' + str(len(datagram) - 6) + 's', datagram)
