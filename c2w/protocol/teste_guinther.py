import struct 


class Room():
    def __init__(self,room_id,ip_string,port_number,name,nbr_users):
        self.room_id = room_id ;
        self.ip_string = ip_string; #177.22.22.1
        self.port_number = port_number;
        self.name = name;
        self.nbr_users = nbr_users;

    def getListIP (self):
        list_ip = self.ip_string.split('.',maxsplit=3);
        list_ip = list(map(int, list_ip))
        return list_ip;

room1 = Room(13,'177.22.22.1',8888,'Animaux Fantastique',30);

print(room1.getListIP());

print(str(hex(8888)))
