# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import logging

import c2w
from c2w.main.lossy_transport import LossyTransport

import time
import c2w.main.constants

from . import unpacking
from . import packing
import struct
import math
from . import misc
from twisted.internet import reactor
from c2w.main.client_model import c2wClientModel
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.tcp_chat_server_protocol')


class c2wTcpChatServerProtocol(Protocol):

    def __init__(self, serverProxy, clientAddress, clientPort):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param clientAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param clientPort: The port number used by the c2w server,
            given by the user.

        Class implementing the TCP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: clientAddress

            The IP address of the client corresponding to this 
            protocol instance.

        .. attribute:: clientPort

            The port number used by the client corresponding to this 
            protocol instance.

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.

        .. note::
            The IP address and port number of the client are provided
            only for the sake of completeness, you do not need to use
            them, as a TCP connection is already associated with only
            one client.
        """
        #: The IP address of the client corresponding to this 
        #: protocol instance.
        self.clientAddress = clientAddress
        #: The port number used by the client corresponding to this 
        #: protocol instance.
        self.clientPort = clientPort
        #: The serverProxy, which the protocol must use
        #: to interact with the user and movie store in the server.
        self.serverProxy = serverProxy
        self.buffer = bytearray(0) # Only save the incomplete part of a message
        
        self.events_list = {}
        self.last_event_ID = -1
        self.seq_number_users = {}   

    def loginRules(self, username):
        # Cette function limite les caractères, la taille et la forme d'username
        # return TRUE si le username est bon
        # return FALSE si le username n'est pas bon
        return 1

    def getRooms(self, first_room_id, nbr_rooms):   ######################################################## Il faut commenter
    
        movie_list = self.serverProxy.getMovieList()
        users_list = self.serverProxy.getUserList()
        

        movie_id_selected = []
        for movie in movie_list :
            if movie.movieId >= first_room_id :
                movie_id_selected.append(movie.movieId)

                
        movie_id_sorted_list = sorted(movie_id_selected, key=int)
        
        if nbr_rooms > len(movie_id_sorted_list) :
            movie_id_sorted_list = movie_id_sorted_list[0:nbr_rooms]
        else :
            movie_id_sorted_list = movie_id_sorted_list[0:len(movie_id_sorted_list)]    
        
        movie_list_to_response_rooms = []
        n_users_room = [] # il faut faire un vecteur de zeros
        
        for i in range(len(movie_id_sorted_list)) :
            movie_list_to_response_rooms.append(self.serverProxy.getMovieById(movie_id_sorted_list[i]))
            n_users_room.append(0)
            for users in users_list :
                if users.userChatRoom == movie_id_sorted_list[i] :
                    n_users_room[i] = n_users_room[i] + 1
                    
                    
        print(str(len(movie_list_to_response_rooms))+ "," + str(len(n_users_room)))                  
                    
        return [movie_list_to_response_rooms, n_users_room]

    def addEvent(self, event_type, user_id, content):
        # Je dois créer une dictionary avec tous les events
        # Je dois créer une variable current_event
        # La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        # Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        # Si on arrive au fin de la dictionary on doit commencer par zero de nouveau
        # On va écrire sur les anciennes contenue de les clés
        # Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        # faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        # faire une fonction pour recueillir les événements de first_event to last_event de la liste

        # event_type = 0x01 # MESSAGE # content = message(String)
        # event_type = 0x02 # NEW_USER # content = username(String)
        # event_type = 0x03 # SWITCH_ROOM # content = new_room_id
        # event_type = 0x04 # LOGOUT # content = None
                
        room_id = self.serverProxy.getUserById(user_id).userChatRoom    # On récupere le room_id du usager
        
        if self.last_event_ID == 16777215 :                             # Si on arrive à la fin, on retourne au débout
            event_id = 0
        else :                                                          # Sinon on incremente
            event_id =  self.last_event_ID + 1
           
        coded_event = packing.CODE_EVENT(event_type, event_id, room_id, user_id, content)   # code le event
        self.events_list[event_id] = coded_event                                  # on enregistre le event sur le bon champ
        
        self.last_event_ID = event_id                                             # On incremente self.last_event_ID
        
        print(coded_event) 

###########
              
    def getEvent(self,last_event_id,room_id,nbr_events): ######################################################## Il faut commenter
        # Je dois créer une list/dictionary avec tous les events
        # Je dois créer une variable current_event
        # La clés sera le event_number et le contenu sera le paquet, déjà dans la forme binaire pour ajouter dans la réponse RESPONSE_EVENTS
        # Les clés sont numérotés de 0 (/0x00/0x00/0x00) à 16777215 (/0xff/0xff/0xff)
        # Si on arrive au fin de la list/dictionary on doit commencer par zero de nouveau
        # On va écrire sur les anciennes contenue de les clés
        # Paquets du type: NEW_MESSAGE, NEW_USER, SWITCH_ROOM et LOGOUT
        # faire une fonction pour ajouter le événement dans la bonne position, dans la bonne forme de packet, incrementer current_event
        # faire une fonction pour recueillir les événements de first_event to last_event de la liste
       
        #Je n'utilise pas encore room_id, mais, je crois que je vais changer
        
        n_event = last_event_id + 1
        get_events_list = b''   
        real_events_number = 0
        i = 0
        end = False
        while i < nbr_events and not end :
            i += 1
            if n_event == self.last_event_ID :
                get_events_list += self.events_list[n_event]
                real_events_number = real_events_number + 1
                end = True
            elif n_event == 16777215 :
                get_events_list += self.events_list[n_event]
                n_event = 0
                real_events_number = real_events_number + 1
            else :
                get_events_list += self.events_list[n_event]
                n_event = n_event + 1
                real_events_number = real_events_number + 1    
        return [get_events_list, real_events_number]


    def getUsers(self, first_user_id, nbr_users, room_id):
        # l'entrées : le ID du première usager que le client a demandé,
        # le nombre de de usagers et le room où on va chercher
        
        # le résultat : une liste de la classe c2wUser avec le nombre d'usagers demandé dans la bonne salle
        
        users_list = self.serverProxy.getUserList()                                  # On trouve tous les usagers
        
        # i = 0
        user_id_selected = []
        for user in users_list :                                                     # On prend les usagers dans la bonne movie room
            if user.userChatRoom == room_id and user.userId >= first_user_id :
                user_id_selected.append(user.userId)                                    # On prend le id de tous les usagers sélectionnés
        # i = i + 1
                
        user_id_sorted_list = sorted(user_id_selected, key=int)                      # On ordenne le ID des usagers
        
        if nbr_users > len(user_id_sorted_list) :
            user_id_sorted_list = user_id_sorted_list[0:nbr_users]                   # On ne prend que le nombre demandé
        else :
            user_id_sorted_list = user_id_sorted_list[0:len(user_id_sorted_list)]    # On prend le maximum possible
        
        user_list_to_response_users = []                                             # liste vide pour garder le résultat
        
        for i in range(len(user_id_sorted_list)) :
            user_list_to_response_users.append(self.serverProxy.getUserById(user_id_sorted_list[i])) # On prend les objets de la classe c2wUser
                    
        return user_list_to_response_users

    def dataReceived(self, data):
        """
        :param data: The data received from the client (not necessarily
                     an entire message!)

        Twisted calls this method whenever new data is received on this
        connection.
        """
        self.buffer = self.buffer + data
        if len(self.buffer) >= 6:
            header = self.buffer[:6]
            messageInfo = struct.unpack('!BHBH',header)
            messageLength = messageInfo[3] + 6
            if messageLength <= len(self.buffer):
                datagram = self.buffer[:messageLength] # the entire message
                fieldsList = unpacking.decode(datagram)
                print(fieldsList)
                self.buffer = self.buffer[messageLength:] # the rest of the message
                
                message_type = fieldsList[0][0]
                seq_number = fieldsList[0][1]
                user_id = fieldsList[0][2]
                
                ########### LOGIN REQUEST / RESPONSE_LOGIN
                if message_type == 0x00 :                                                                      # On a reçu le message de login
                    new_username = fieldsList[1][0]
                                    
                    if self.loginRules(new_username) == 1:                                                     # Il faut passer par les régles du serveur
                        if  self.serverProxy.userExists(new_username) :                                        # Il y a déjà quelqu'un avec le même username
                            packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x04)     # faire le paquet                                              
                        elif len(self.serverProxy.getUserList()) > 255 :                                       # Le système est plein d'usagers
                            packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x02)     # faire le paquet 
                        elif not self.serverProxy.userExists(new_username) :                                   # Il n'y a personne avec le même username
                            user_id_login = self.serverProxy.addUser(new_username, 1)# c2w.main.constants.ROOM_IDS.MAIN_ROOM) # On ajoute le user à base de données et prendre le id
                            self.addEvent(0x02, user_id_login, new_username)                                   # On ajoute le login à les événements
                            packet = packing.RESPONSE_LOGIN(0, user_id_login, new_username , self.last_event_ID,0x00) # faire le paquet
                            self.seq_number_users[user_id_login] = [0,packet]                                   # On va créer une position pour le user seq_number
                        else :                                                                                  # On ne sait pas ce que se passe
                            packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x01)      # faire le paquet                                 
                    else :                                                                                      # Le username ne passe pas pour les lois du serveur
                        packet = packing.RESPONSE_LOGIN(0, 0, new_username , self.last_event_ID, 0x03)          # faire le paquet
                    
                    self.transport.write(packet)     

                                             # On envoie le paquet       


                ###########        
                if user_id in self.seq_number_users :     
                    if seq_number == self.seq_number_users[user_id][0] + 1 : 
                    ########### LOGOUT REQUEST / RESPONSE_LOGOUT
                        if message_type == 0x02 :                                                           # On a reçu le message de logout
                            print('log out')                            
                            if self.serverProxy.userExists(self.serverProxy.getUserById(user_id).userName): # On vérifie si il y a le user sur la base de données                        
                                self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user  "" Je crois qu'il n'y a pas besoin de faire ça un fois que on utilise pas resendResponse
                                self.addEvent(0x04, user_id, None)                                          # On ajoute le logout à les événements                
                                self.serverProxy.removeUser(self.serverProxy.getUserById(user_id).userName) # On supprime le user (On doit faire ça après addEvent)
                                packet = packing.RESPONSE_LOGOUT(seq_number,user_id,0x00)                   # On fait le paquet 
                                self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet "" Je crois qu'il n'y a pas besoin de faire ça un fois que on utilise pas resendResponse
                                self.transport.write(packet)
                                
                            else :                                                                          # Si on a déjà supprimés le user de la base de données
                                packet = packing.RESPONSE_LOGOUT(seq_number,user_id,0x00)
                                self.transport.write(packet)
                                
                            if self.serverProxy.userExists(self.serverProxy.getUserById(user_id).userName): # Si même après avoir supprimé le user, il existe dans la base de données
                                packet = packing.RESPONSE_LOGOUT(seq_number,user_id,0x01)                   # On fait le paquet 
                                self.transport.write(packet)                                                # On envoie le paquet      

                    ########### PING REQUEST / RESPONSE_PING
                        if message_type == 0x04 :                                                       # On a reçu le message de get_ping
                            packet = packing.RESPONSE_LOGOUT(seq_number, user_id, self.last_event_ID)   # On fait le paquet avec last_event_ID courrant
                            self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                            print('seq number = ',self.seq_number_users[user_id][0])                            
                            self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet
                            self.transport.write(packet)      

                    ########### EVENTS REQUEST / RESPONSE_EVENTS
                        if message_type == 0x06 :                                                       # On a reçu le message de get_events
                            last_event_id = fieldsList[1][0]                                            # Le premier event que le usager demande
                            nbr_events = fieldsList[1][1]                                               # Le nombre de events que le usager demande
                            room_id = fieldsList[1][2]                                                  # La room où le usager demande les events
                            
                            getEvents = self.getEvent(last_event_id,room_id,nbr_events)
                            packet_content = getEvents[0]
                            print(packet_content)                                            # le packet binaire avec tous les events déjà codé (sans le nbr_events)
                            real_events_number = getEvents[1]                                            # Le nombre de events qu'on envoie (pas necessairement le celui demandé)
                            message_length = len(packet_content)                                        # la taille de la message (sans nbr_events, on ajoute ça dans RESPONSE_EVENTS_HEAD)
                            packet_head = packing.RESPONSE_EVENTS_HEAD(seq_number, user_id, real_events_number,message_length) # le packet binaire avec le message head
                            print(packet_head)
                            packet = packet_head + packet_content
                            print(packet)                                                             # On additionne les deux packet binaires
                            
                            self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                            self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet
                            
                            self.transport.write(packet)


                ########### ROOMS REQUEST / RESPONSE_ROOMS
                    if message_type == 0x08 :                                                               # On a reçu le message de get_rooms
                        first_room_id = fieldsList[1][0]                                                    # La première movie room que on va envoyer
                        nbr_rooms = fieldsList[1][1]                                                        # Le nombre de movie room que on va envoyer
                        
                        movie_list = self.getRooms(first_room_id, nbr_rooms)[0]                                  # Une liste avec les classes c2wMovie qu'on va envoyer
                        n_users_room_list = self.getRooms(first_room_id, nbr_rooms)[1]                           # Une liste avec le nombre de usagers dans chaque movie room
                        
                        
                        packet = packing.RESPONSE_ROOMS(seq_number, user_id, movie_list, n_users_room_list) # On fait le paquet
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1           # On incrémente le seq_number du user              
                        self.seq_number_users[user_id][1] = packet                                          # On enregistre le paquet
                        self.transport.write(packet)                                                        # On envoie le paquet  


                ########### USERS REQUEST / RESPONSE_USERS
                    if message_type == 0x0A :                                                      # On a reçu le message de get_users
                        first_user_id = fieldsList[1][0]                                           # Le première user que on va envoyer
                        nbr_users = fieldsList[1][1]                                               # Le nombre de users que on va envoyer
                        
                        user_list = self.getUsers(first_user_id, nbr_users, self.serverProxy.getUserById(user_id).userChatRoom)                             
                        # Une liste avec les classes c2wUser qu'on va envoyer
                        
                        packet = packing.RESPONSE_USERS(seq_number, user_id, user_list)            # On fait le paquet
                        
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1  # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                 # On enregistre le paquet
                        self.transport.write(packet)   



                ########### SWITCH ROOM REQUEST / RESPONSE_SWITCH_ROOM
                    if message_type == 0x0C :                                                       # On a reçu le message de get_users
                        username = self.serverProxy.getUserById(user_id).userName                   # Le nom d'usager
                        old_room = self.serverProxy.getUserById(user_id).userChatRoom               # L'ancienne room
                        new_room = fieldsList[1][0]                                                 # la nouvelle room
                        
                        if self.serverProxy.getMovieById(new_room) :                                # S'il existe la room dans le système 
                            self.serverProxy.updateUserChatroom(username, new_room)                 # On met à jour la room
                        
                            if new_room == self.serverProxy.getUserById(user_id).userChatRoom :     # On a bien mis à jour la room
                                self.addEvent(0x03, user_id, old_room)                              # On ajoute à les events     
                                packet = packing.RESPONSE_SWITCH_ROOM(seq_number, user_id, 0x00)    # On fait le paquet
                            else :
                                packet = packing.RESPONSE_SWITCH_ROOM(seq_number, user_id, 0x01)    # On fait le paquet
                                
                        else :                                                                      # Il existe pas le movie room (manque le bon code)
                            packet = packing.RESPONSE_SWITCH_ROOM(seq_number, user_id, 0x01)        # On fait le paquet                    
                            
                        self.seq_number_users[user_id][0] = self.seq_number_users[user_id][0] + 1   # On incrémente le seq_number du user
                        self.seq_number_users[user_id][1] = packet                                  # On enregistre le paquet  
                        self.transport.write(packet)                                                # On envoie le paquet           



