import socket
import threading
import SocketServer


#Threaded client request handler
class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        response = "{}: {}".format(cur_thread.name, data)
        self.request.sendall(response)

#Threaded TCP Server class
class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

    
#IOTP server wrapper    
class IOTPTServerCore:
    def __init__(self, port = 0, host = "localhost"): # 0 indicates any free port
        self.PORT = port
        hostname = socket.gethostname()   
        IPAddr = socket.gethostbyname(hostname)        
        self.HOST = IPAddr
        self.server = None        
        
    def start(self): 
        if self.server == None:
            self.server = ThreadedTCPServer((self.HOST, self.PORT), ThreadedTCPRequestHandler)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.ip, self.port = self.server.server_address
                        
            print "Server IP " + IPAddr
            print "Server PORT " + str(self.port)
            # Start a thread with the server -- that thread will then start one
            # more thread for each request
            self.server_thread = threading.Thread(target = self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
        
    def stop(self):
        if self.server != None and self.server_thread.daemon == True:
            self.server.shutdown()
            self.server.server_close()