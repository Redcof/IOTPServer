__author_ = "int_soumen"
_date_ = "29-07-2018"


class IOPTServiceType:
    def __init__(self):
        pass

    UNKNOWN = 0
    BYTE = 1
    IOTP = 2
    HTTP = 3


class IOTPRequestComponent:
    def __init__(self):
        pass

    SLAVE_ID = "slv_id"
    SLAVE_QUERY = "slv_qer"
    DIGITAL_OPERAND_ID = "digt_id"
    DIGITAL_OPERAND_QUERY = "digt_qer"
    DIGITAL_OPERAND_STATUS = "digt_st"
    ANALOG_OPERAND_ID = "anlg_id"
    ANALOG_OPERAND_QUERY = "anlg_qer"
    ANALOG_OPERAND_VALUE = "anlg_val"


class IOTPRequest:
    def __init__(self):
        self.service_type = IOPTServiceType.UNKNOWN
        self.keep_conn = False
        self.chunk_size = 0
        self.connection = None
        self.ip = None

    def set_connection(self, conn):
        self.connection = conn

    def set_ip(self, ip):
        self.ip = ip

    def initiate_connection(self, formatted_data):
        if self.service_type is IOPTServiceType.BYTE:
            self.connection.send("byte init OK\n")
            # TODO Slave Validation :
            # slave id, number of digital operand
            # and number of analog operand
            # validate slave id uniqueness and range
            # otherwise reject the connection
            # if everything goes fine, store slav information,
            #  send conformation  byte to slave, as the slave
            #  has been accepted
        elif self.service_type is IOPTServiceType.IOTP:
            self.connection.send("iotp init OK\n")
        elif self.service_type is IOPTServiceType.HTTP:
            pass

    def callback(self, formatted_data):
        if self.service_type is IOPTServiceType.BYTE:
            pass
            # TODO Parse slave bytes
            # if it is require then send
            # a response to IOTP Service or HTTP service
            # or Push Service
        elif self.service_type is IOPTServiceType.IOTP:
            pass
            # TODO Parse IOTP request
            # and generate byte for slave
            # device requested, send the bytes to slave
            # and wait for reply from salve
        elif self.service_type is IOPTServiceType.HTTP:
            pass
            # TODO Parse IOTP request
            # and generate byte for slave
            # device requested, send the bytes to slave
            # and wait for reply from salve

    def set_type(self, service_type):
        self.service_type = service_type
        if self.service_type is IOPTServiceType.BYTE:
            self.keep_conn = True
            self.chunk_size = 64

        elif self.service_type is IOPTServiceType.IOTP:
            self.chunk_size = 128

        elif self.service_type is IOPTServiceType.HTTP:
            self.chunk_size = 128
