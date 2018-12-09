import IOTPServer as int_serve

bServer_status = False
iotp_server = None

def iotp_help(options = []):
    for key, value in _cmd_map.iteritems() :
        print key, ":" ,  value[0]
    
def iotp_start(options = ["107"]):
    global bServer_status
    global iotp_server
    if bServer_status == False:
        try:
            port = options[0].strip()
            if port == "":
                port = 107            
        except:
            port = 107
        print "Starting server..."
        iotp_server = int_serve.IOTP_ServerCore(int(port))
        iotp_server.start()
        bServer_status = True
        print "Server is started at " + str(port)
        
    else:
        print "Server already running."
    
def iptp_stop(options = []):
    global bServer_status
    global iotp_server
    if bServer_status == True:
        print "Closing server..."
        iotp_server.stop()
        bServer_status = False
        print "Server is closed."
    
def iptp_stat(options = []):
    global bServer_status
    if bServer_status == True:
        print "Server is online."
    else:
        print "Server is closed."
    
_cmd_map = {
    "-h" : ["""Get all available commands options. 
    [] is for optional parameters.
    <> is for required parameters.    
    """, iotp_help],
    "start" : [""" start<space>[port]
    To start the  IOTP server. Default port is 107. 
    It is often require root access to start the server.
              """, iotp_start],
    "stop" : [""" stop 
    To stop the IOTP server""", iptp_stop]  ,
    "stat" : [""" stat 
    To get the IOTP server status""", iptp_stat]    
}