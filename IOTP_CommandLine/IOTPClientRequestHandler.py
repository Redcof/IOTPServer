from IOTP_ServerCore.IOTPRequest import IOTPRequest, IOPTServiceType


class IOTPClientRequestHandler(IOTPRequest):
    def __init__(self):
        IOTPRequest.__init__(self)

    def callback(self, connection, client_ip, formatted_data):
        print formatted_data
        connection.send("OK\n")