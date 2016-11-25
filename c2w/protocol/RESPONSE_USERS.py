import struct 


class User():
    def __init__(self,user_id,username,room_id):
        self.user_id = user_id ;
        self.username = username;
        self.room_id = room_id;


def RESPONSE_USERS(seq_number,user_id,users_list):

# Function to struct the PUT_NEW_MESSAGE packet
# MESSAGE_TYPE (1 byte 'B') = 14 (0x0E)
# SEQ_NUMBER (2 byte 'H')
# USER_ID (1 byte 'B')
# MESSAGE1_LENGTH (2 byte 'H') = 3 + MESSAGE2_LENGTH (1 for ROOM_ID and 2 for MESSAGE2_LENGTH)
# ROOM_ID (1 byte 'B')
# MESSAGE2_LENGTH (2 byte 'H') = size of MESSAGE
# MESSAGE (MESSAGE2_LENGTH bytes 's')
    
    message_type = 0x0B;
    nbr_users = len(users_list);

    code = '!BHBH' + 'BH';

    list_length = 0;



    for user in users_list:
        user_length = len(user.username);
        list_length = list_length + 3 + user_length;

    
    message_length = list_length + 1;   
    data = bytearray(6+message_length);
    
    code = '!BHBH' + 'B';
    offset = 0;
    struct.pack_into(code,data,offset,message_type,seq_number,user_id,message_length,nbr_users);

    for i in range(nbr_users):
        user_id = users_list[i].user_id;
        username = users_list[i].username;
        room_id = users_list[i].room_id;

        user_length = len(users_list[i].username);
        
        if i == 0:
            offset = 7; 
        else:
            offset = offset + 3 + len(users_list[i-1].username);
        
        code = 'BB'+ str(user_length) + 's' + 'B';
        struct.pack_into(code,data,offset,user_id,user_length,username.encode('utf-8'),room_id);

    return data;



client1 = User(0,'Guinther',0);
client2 = User(1,'Louis',7);
client3 = User(2,'Remy',0);
client4 = User(3,'Anq',3);

lista = [client1,client2,client3,client4];

A = RESPONSE_USERS(7,15,lista);
print(A);

