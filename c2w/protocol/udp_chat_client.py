# -*- coding: utf-8 -*-*
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')
import time
from . import unpacking
#from PUT_LOGIN import PUT_LOGIN
from . import PUT_LOGIN
#from . import resent_login
from twisted.internet import reactor
from c2w.main.client_model import c2wClientModel


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        self.seq_number = 0
        self.userID = 0
        self.lastEventID = 0
        self.successful_login = 0;
        self.store = c2wClientModel();
        self.delay = 1; #1s

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport;

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGIN packet to the server
        # - Re-emit it if the timer ran out
        moduleLogger.debug('loginRequest called with username=%s', userName)
        packet = PUT_LOGIN.PUT_LOGIN(self.seq_number,userName)      
        self.transport.write(packet, (self.serverAddress, self.serverPort))
              
        #reactor.callLater(self.delay, self.resent_login,packet);
    


    def resent_login(packet):

        if successful_login == 0: # packet lost
            transport.write(packet,(self.serverAddress,self.serverPort))
            #reactor.callLater(self.delay, self.resent_login, packet)
            print(1)
        


    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_NEW_MESSAGE packet to the server
        # - Re-emit it if the timer ran out
        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_SWITCH_ROOM with the roomName field packet to the server
        # - Re-emit it if the timer ran out
        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        #This function should :
        # - Arm a timer
        # - Send a correctly formed PUT_LOGOUT packet to the server
        # - Re-emit it if the timer ran out
        pass

    def datagramReceived(self, datagram, host_port):


        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """

        #This function should :
        # - Unpack the datagram
        # - Read the  SEQ_NUMBER and MESSAGE_TYPE fields in the header
        # - If the SEQ_NUMBER is the one that is awaited, proceed, if not stop right there
        # - Disarm the timer that was armed with the last sendRequest
        # - Select the correct following function to read the unpacked datagram based on MESSAGE_TYPE field


        fieldsList = unpacking.decode(datagram)
        if fieldsList[0][1] == self.seq_number : #Le message reçu est celui-attendu
            if fieldsList[0][0] == 1 : #Le message reçu est de type RESPONSE_LOGIN            
                self.successful_login = 1;            
                if fieldsList[1][0] == 0 : #Status code = success
                    self.userID = fieldsList[1][1]
                    self.lastEventID = fieldsList[1][2]
                    self.seq_number +=1
                elif fieldsList[1][0] == 1 :
                    self.clientProxy.connectionRejectedONE('Unknow error');
                elif fieldsList[1][0] == 2 :
                    self.clientProxy.connectionRejectedONE('Too many users');
                elif fieldsList[1][0] == 3 :
                    self.clientProxy.connectionRejectedONE('Invalid username');
                elif fieldsList[1][0] == 4 :
                    self.clientProxy.connectionRejectedONE('Username not available');
                else :
                    self.clientProxy.connectionRejectedONE('Impossible to interpret RESPONSE_LOGIN');                    
"""               
            elif fieldsList[0][0] == 3 : #Le message reçu est de type RESPONSE_LOGOUT
                self.userID = 0;
                self.lastEventID = 0;
                self.seq.number = 0;
                self.successful_login = 0;
                self.store.removeAllMovies();
                self.store.removeAllUsers();
                    
            elif fieldsList[0][0] == 5 : #Le message reçu est de type RESPONSE_PING
                pass
                    
            elif fieldsList[0][0] == 7 : #Le message reçu est de type RESPONSE_EVENTS
                pass

            elif fieldsList[0][0] == 9 : #Le message reçu est de type RESPONSE_ROOMS
                for i in range(len(fieldsList)):
                    if store.getMovieById(fieldsList[1+i][3]) == None:   
                        store.addMovie(fieldsList[1+i][3],fieldsList[1+i][1], fieldsList[1+i][2], fieldsList[1+i][0],fieldsList[1+i][4]);
            #Returned in the following form : Room_id, IP, Port, Room_name, Nbr_users                


            elif fieldsList[0][0] == 11 : #Le message reçu est de type RESPONSE_USERS
                pass

            elif fieldsList[0][0] == 13 : #Le message reçu est de type RESPONSE_SWITCH_ROOM
                pass

            elif fieldsList[0][0] == 15 : #Le message reçu est de type RESPONSE_NEW_MESSAGE
                pass
            
     
        
    
                
"""             
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
                
