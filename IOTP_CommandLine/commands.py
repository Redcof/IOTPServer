from IOTP_CommandLine import IOTPClientRequestHandler as iotp_req_handle
from IOTPServerCore import IOTPServer as int_serve

bServer_status = False
iotp_server = None



def iotp_help(options=[]):
    for key, value in cmd_map.iteritems():
        print key, ":", value[0]


def iotp_start(options=()):
    global bServer_status
    global iotp_server
    if bServer_status is False:
        print "Starting server..."
        # initialize request handler class
        iotp_req = iotp_req_handle.IOTPClientRequestHandler()
        # initialize server object
        if len(options) == 1:
            iotp_server = int_serve.IOTPServerCore(iotp_req, int(options[0]))
        else:
            iotp_server = int_serve.IOTPServerCore(iotp_req)
        # start server
        if iotp_server.start() is True:
            bServer_status = True
            print "Server is started"


    else:
        print "Server already running."


def iptp_stop(options=[]):
    global bServer_status
    global iotp_server
    if bServer_status is True:
        print "Closing server..."
        iotp_server.stop()
        bServer_status = False
        print "Server is closed."


def iptp_stat(options=[]):
    global bServer_status
    if bServer_status is True:
        print "Server is online."
    else:
        print "Server is closed."


cmd_map = {
    "-h": ["""Get all available commands options. 
    [] is for optional parameters.
    <> is for required parameters.    
    """, iotp_help],
    "start": [""" start[<space>port[<space>localhost]]
    To start the  IOTP server. Default port is 10700. 
    It is often require root access to start the server.
              """, iotp_start],
    "stop": [""" stop 
    To stop the IOTP server""", iptp_stop],
    "stat": [""" stat 
    To get the IOTP server status""", iptp_stat]
}
