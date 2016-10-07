# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol


class SibylServerUdpTextProtocol(DatagramProtocol):
    """The class implementing the Sibyl UDP text server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives a
            datagram):
            :py:meth:`~sibyl.main.protocol.sibyl_server_udp_text_protocol.datagramReceived`
            See the corresponding documentation below.

    This class has the following attribute:

    .. attribute:: SibylServerProxy

        The reference to the SibylServerProxy (instance of the
        :py:class:`~sibyl.main.sibyl_server_proxy.SibylServerProxy` class).

            .. warning::

                All interactions between the client protocol and the server
                *must* go through the SibylServerProxy.

    """

    def __init__(self, sibylServerProxy):
        """The implementation of the UDP server text protocol.

        Args:
            sibylServerProxy: the instance of the server proxy.
        """
        self.sibylServerProxy = sibylServerProxy

    def datagramReceived(self, datagram, host_port):
        """Called by Twisted whenever a datagram is received

        Twisted calls this method whenever a datagram is received.

        Args:
            datagram (bytes): the payload of the UPD packet;
            host_port (tuple): the source host and port number.

            .. warning::
                You must implement this method.  You must not change the
                parameters, as Twisted calls it.

        """
        print(datagram)
        decodedMessage = datagram.decode('utf-8')
        print(decodedMessage)
        splitedMessage = decodedMessage.split(': ', 1)
        print(splitedMessage[1])
        randomResponse = self.sibylServerProxy.generateResponse(splitedMessage[1]) 
        print(randomResponse)
        
        sendResponse = splitedMessage[0] + ": " + randomResponse + "CRLF"
        print(sendResponse)
        codedResponse = sendResponse.encode('utf-8')
        print(codedResponse)
        self.transport.write(codedResponse, host_port)

        pass



    
