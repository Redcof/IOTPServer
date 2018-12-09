# Python program to implement server side of chat room.
import socket
import select
import sys
from thread import *

#"""The first argument AF_INET is the address domain of the
#socket. This is used when we have an Internet Domain with
#any two hosts The second argument is the type of socket.
#SOCK_STREAM means that data or characters are read in
#a continuous flow."""
#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

## checks whether sufficient arguments have been provided
#if len(sys.argv) != 3:
    #print "Correct usage: script, IP address, port number"
    #exit()

## takes the first argument from command prompt as IP address
#IP_address = str(sys.argv[1])

## takes second argument from command prompt as port number
#Port = int(sys.argv[2])

#"""
#binds the server to an entered IP address and at the
#specified port number.
#The client must be aware of these parameters
#"""
#server.bind((IP_address, Port))

#"""
#listens for 100 active connections. This number can be
#increased as per convenience.
#"""
#server.listen(100)

#list_of_clients = []

#def clientthread(conn, addr):
    ## sends a message to the client whose user object is conn
    #while True:
        #try:
            #message = conn.recv(128)
            #if message:

                #"""prints the message and address of the
                    #user who just sent the message on the server
                    #terminal"""
                #message_to_send = "<" + addr[0] + "> " + message
                #print message_to_send

                ### Calls broadcast function to send message to all                
                ### broadcast(message_to_send, conn)
                
                ##Send message to client
                #try:
                    #conn.send(message)
                #except:
                    ## if the link is broken, we remove the client
                    ##conn.close()  #No need of close as link is already broken                   
                    #remove(conn)
                    #break

            #else:
                #"""message may have no content if the connection
                    #is broken, in this case we remove the connection"""
                #remove(conn)

        #except:
            #continue

#"""Using the below function, we broadcast the message to all
#clients who's object is not the same as the one sending
#the message """
#def broadcast(message, connection):
    #for clients in list_of_clients:
        #if clients != connection:
            #try:
                #clients.send(message)
            #except:
                #clients.close()

                ## if the link is broken, we remove the client
                #remove(clients)

#"""The following function simply removes the object
#from the list that was created at the beginning of 
#the program"""
#def remove(connection):
    #if connection in list_of_clients:
        #list_of_clients.remove(connection)

#while True:
    #"""Accepts a connection request and stores two parameters, 
    #conn which is a socket object for that user, and addr 
    #which contains the IP address of the client that just 
    #connected"""
    #conn, addr = server.accept()

    #"""Maintains a list of clients for ease of broadcasting
    #a message to all available people in the chatroom"""
    #list_of_clients.append(conn)

    ## prints the address of the user that just connected
    #print addr[0] + " connected"

    ## creates and individual thread for every user 
    ## that connects
    #start_new_thread(clientthread,(conn,addr))    

#conn.close()
#server.close()



#IOTP server wrapper    
class IOTP_ServerCore:
    
    def __init__(self, port = 0, ip = None, backlog = 20): # 0 indicates any free port
        self.PORT = port
        if ip == None:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
        self.IP = ip
        self.BACK_LOG = backlog
        self.server = None
        self.list_of_clients = []
        print "Server IP " + ip
        
    def start(self): 
        if self.server == None:
            """The first argument AF_INET is the address domain of the
socket. This is used when we have an Internet Domain with
any two hosts The second argument is the type of socket.
SOCK_STREAM means that data or characters are read in
a continuous flow."""
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            """
            binds the server to an entered IP address and at the
            specified port number.
            The client must be aware of these parameters
            """
            self.server.bind((self.IP, self.PORT))
            start_new_thread(self.s_listen, ())
            
    def s_listen(self):
        """
        listens for 'BACK_LOG' active connections. This number can be
        increased as per convenience.
        """
        self.server.listen(self.BACK_LOG)
        
        while True:
            """Accepts a connection request and stores two parameters, 
            conn which is a socket object for that user, and addr 
            which contains the IP address of the client that just 
            connected"""
            conn, addr = self.server.accept()
        
            """Maintains a list of clients for ease of broadcasting
            a message to all available people in the chatroom"""
            self.list_of_clients.append(conn)
        
            # prints the address of the user that just connected
            print addr[0] + " connected"
        
            # creates and individual thread for every user 
            # that connects
            start_new_thread(self.clientthread, (conn,addr))        
    
    def stop(self):
        if self.server != None:
            for connection in list_of_clients:
                connection.close()
                list_of_clients.remove(connection)
            self.server.close()
            
    def clientthread(self,conn, addr):
        # sends a message to the client whose user object is conn
        while True:
            try:
                message = conn.recv(128)
                if message:
    
                    """prints the message and address of the
                        user who just sent the message on the server
                        terminal"""
                    message_to_send = "<" + addr[0] + "> " + message
                    print message_to_send
    
                    ## Calls broadcast function to send message to all                
                    ## self.broadcast(message_to_send, conn)
                    
                    #Send message to client
                    try:
                        conn.send(message_to_send)
                    except:
                        # if the link is broken, we remove the client
                        #conn.close()  #No need of close as link is already broken                   
                        self.remove(conn)
                        break
    
                else:
                    """message may have no content if the connection
                        is broken, in this case we remove the connection"""
                    self.remove(conn)
                    break
    
            except:
                continue
        print addr[0] + "Closed."
    
    """Using the below function, we broadcast the message to all
    clients who's object is not the same as the one sending
    the message """
    def broadcast(self,message, connection):
        for clients in self.list_of_clients:
            if clients != connection:
                try:
                    clients.send(message)
                except:
                    clients.close()
    
                    # if the link is broken, we remove the client
                    self.remove(clients)
    
    """The following function simply removes the object
    from the list that was created at the beginning of 
    the program"""
    def remove(self,connection):
        if connection in self.list_of_clients:
            self.list_of_clients.remove(connection)    