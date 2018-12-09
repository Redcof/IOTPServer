import socket

#this function is a complete client implementation
def client(ip, port, message):
    hostname = socket.gethostname()   
    IPAddr = socket.gethostbyname(hostname)            
    print "Client IP " + IPAddr      
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()
        

client("192.168.0.108", 107, "message Lorem")