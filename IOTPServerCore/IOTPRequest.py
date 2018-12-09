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

    def callback(self, connection, client_ip, formatted_data):
        connection.send("OK\n")

    def set_type(self, service_type):
        self.service_type = service_type
        if self.service_type is IOPTServiceType.BYTE:
            self.keep_conn = True
            self.chunk_size = 64

        elif self.service_type is IOPTServiceType.IOTP:
            self.chunk_size = 128

        elif self.service_type is IOPTServiceType.HTTP:
            self.chunk_size = 128
