_author_ = "int_soumen"
_date_ = "27-07-2018"


# IOTP Request Types
class IOPTServiceType:
    pass
    UNRESOLVED = 0
    BYTE = 1  # data will be exchanged in plain byte
    IOTP = 2  # data will be exchange with UCI start with iotp://
    HTTP = 3  # data will be exchanged with HTTP Protocol


# IOTP Request Handler class
class IOTPRequest():

    def __init__(self):
        self.type = IOPTServiceType.UNRESOLVED
        self.keep_alive = False
        self.BYTES_READ = 0
        self.switcher = {
            # [0] -> keep_alive [1] -> chunk_size
            IOPTServiceType.UNRESOLVED: [False, 0],
            IOPTServiceType.BYTE: [True, 128],
            IOPTServiceType.IOTP: [False, 1024],
            IOPTServiceType.HTTP: [False, 2048],
        }

    # set the request type
    def setType(self, req_type):
        if type(req_type) is IOPTServiceType:
            self.type = req_type
            self.keep_alive = self.switcher.get(self.type)[0]
            self.BYTES_READ = self.switcher.get(self.type)[1]

    # request handle callback
    def callback(self, connection, client_ip, formatted_data):
        if self.type == IOPTServiceType.IOTP:
            connection.send("OK\n")
