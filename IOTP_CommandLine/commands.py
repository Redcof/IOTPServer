from IOTP_CommandLine import IOTPClientRequestHandler as iotp_req_handle
from IOTPServerCore import IOTPServer as int_serve
from IntsUtil.util import log

bServer_status = False
iotp_server = None


def iotp_help(options=[]):
    for key, value in cmd_map.iteritems():
        print key, ":", value[0]


def iotp_start(server_home, options=()):
    global bServer_status
    global iotp_server
    if bServer_status is False:
        log("Starting server...", False)
        # initialize request handler class
        iotp_req = iotp_req_handle.IOTPClientRequestHandler()
        # initialize server object
        if len(options) == 1:
            iotp_server = int_serve.IOTPServerCore(iotp_req, server_home, int(options[0]))
        else:
            iotp_server = int_serve.IOTPServerCore(iotp_req, server_home)
        # blink server
        s = iotp_server.start()
        if s is True:
            bServer_status = True
            log( "Server is started", False)
        else:
            return False
    else:
        log( "Server already running.", False)
    return True


def iptp_stop(options=()):
    global bServer_status
    global iotp_server
    if bServer_status is True:
        log( "Closing server...", False)
        iotp_server.stop_blink()
        bServer_status = False
        log( "Server is closed.", False)


def iptp_stat(options=()):
    global bServer_status
    if bServer_status is True:
        log( "Server is online.", False)
    else:
        log( "Server is closed.", False)


cmd_map = {
    "-h": ["""Get all available commands options. 
    [] is for optional parameters.
    <> is for required parameters.    
    """, iotp_help],
    "blink": [""" blink[<space>port[<space>localhost]]
    To blink the  IOTP server. Default port is 10700. 
    It is often require root access to blink the server.
              """, iotp_start],
    "stop_blink": [""" stop_blink 
    To stop_blink the IOTP server""", iptp_stop],
    "stat": [""" stat 
    To get the IOTP server status""", iptp_stat]
}
