

def resent_login(seq_number,username,successful_login,transport,packet,serverAddress,serverPort,delay):

    if successful_login == 0: # packet lost
        transport.write(packet,(serverAddress,serverPort))
        reactor.callLater(delay, resent_login.resent_login,self.seq_number,username,successful_login,transport,packet,serverAddress,serverPort,delay)
        print(1)
        
















