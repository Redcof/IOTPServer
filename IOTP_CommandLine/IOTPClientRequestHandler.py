
from IOTPServerCore.IOTPRequest import IOTPRequest, IOTPRequestComponent, IOPTServiceType

_author_ = 'int_soumen'
_date_ = "27-07-2018"


class IOTPClientRequestHandler( IOTPRequest):
    pass

    def __init__(self):
        IOTPRequest.__init__(self)

    def callback(self, formatted_data):
        IOTPRequest.callback(self, formatted_data)
        print formatted_data

        if self.service_type is IOPTServiceType.IOTP:
            pass
            # check IOTPRequestComponent.SLAVE_QUERY is None, this is a command
