import struct

class Room():


    def __init__(self,room_id,ip_string,port_number,name,nbr_users):
        self.room_id = room_id ;
        self.ip_string = ip_string; #177.22.22.1
        self.port_number = port_number;
        self.name = name;
        self.nbr_users = nbr_users;
        self.list_ip = ip_string.split('.',maxsplit=3);
        self.list_ip = list(map(int, list_ip))


def RESPONSE_ROOMS(seq_number,user_id,rooms_list):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x09;
    nbr_rooms = len(rooms_list);

    list_length = 0;

    for rooms in rooms_list:
        room_length = len(rooms.name);
        list_length = list_length + 9 + room_length;

    
    message_length = list_length + 1;   
    data = bytearray(6+message_length);
    
    code = '!BHBH' + 'B';
    offset = 0;
    struct.pack_into(code,data,offset,message_type,seq_number,user_id,message_length,nbr_rooms);

    for i in range(nbr_rooms):
        room_id = rooms_list[i].room_id;
        ip_numb = rooms_list[i].list_ip;
        port_number = rooms_list[i].port_number;
        name = rooms_list[i].name;
        nbr_users = rooms_list[i].nbr_users;

        room_name_length = len(rooms_list[i].name);
        
        if i == 0:
            offset = 7; 
        else:
            offset = offset + 9 + len(rooms_list[i-1].name);
        
        code = 'B'+'BBBB'+'HB'+ str(room_name_length) + 's' + 'B';
        struct.pack_into(code,data,offset,room_id,ip_number,ip_number[0],ip_number[1],ip_number[2],ip_number[3],room_name_length,name.encode('utf-8'),nbr_users);

    return data;

class Room():
    def __init__(self,room_id,ip_number,port_number,name,nbr_users):
        self.room_id = room_id ;
        self.ip_number = ip_number;
        self.port_number = port_number;
        self.name = name;
        self.nbr_users = nbr_users;

room1 = Room(13,'177.22.22.1',8888,'Animaux Fantastique',30);

lista = [room1];

A = RESPONSE_ROOMS(7,15,lista);
print(A);
