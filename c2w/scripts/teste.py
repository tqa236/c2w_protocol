import struct




message_type = 9
seq_number = 3
user_id = 4
message_length = 1 + 2*(1 + 4 + 2 + 1 + 5 + 1)

nbr_user = 2
room_id = [1,2]
IP = [12,12,12,12]
port = 15
size = 5
nom2 = "poter"
nbr = 2


code = '!BHBH' + 'B'
datagram = struct.pack(code,message_type,seq_number,user_id,message_length,nbr_user)
code = '!B' + 'BBBB' + 'HB' + str(size) + 'sB'
datagram += struct.pack(code,room_id[1],IP[0],IP[1],IP[2],IP[3],port,size,nom2.encode('utf-8'),nbr)
code = '!B' + 'BBBB' + 'HB' + str(size) + 'sB'
datagram += struct.pack(code,room_id[1],IP[0],IP[1],IP[2],IP[3],port,size,nom2.encode('utf-8'),nbr)


def decodeIpAdress(part1, part2, part3, part4) :
    data = str(part1) + '.' + str(part2) + '.' + str(part3) + '.' + str(part4)
    return data
    
def decodeRooms(entryNumber, datagram):

    #This function should :
    # - Unpack a Rooms response datagram
    resultList = []
    for i in range(entryNumber) : #Room (room_id, IP, Port, name_length, room_name, nbr_users)
        print(datagram[:8])
        information = struct.unpack('!BBBBBHB', datagram[:8])
        ipAdress = decodeIpAdress(information[1], information[2], information[3], information[4])
        print(datagram[8:8 + information[6] + 1])
        room_content = struct.unpack('!'+str(information[6])+'s'+'B',datagram[8:8 + information[6] + 1])
        print("##########################################################################" + str(information[6] + 1))
        resultList.append([information[0], ipAdress, information[5], room_content[0].decode('utf-8'), room_content[1]]) #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users
        datagram = datagram[(9+information[6]):]
    return resultList;
    
    
 
#RESPONSE_ROOMS

fieldsList = []
messageHeader = struct.unpack('!BHBH', datagram[:6]) #Contains : messageType, seq_number, user_id, message_length
fieldsList.append(messageHeader)
    
if messageHeader[0] == 9 :
    nbrRooms = struct.unpack('!B', datagram[6:7])
    fieldsList.append(decodeRooms(nbrRooms[0], datagram[7:]))
    
    
print(fieldsList)
