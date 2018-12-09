import re as regex

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


class ByteRequestComponent:
    def __init__(self):
        pass

    SLAVE_ID = "slv_id"
    DIGITAL_COUNT = "digt_ctr"
    ANALOG_COUNT = "anlg_ctr"


def get_max_salve():
    return 25


class IOTPRequest:

    def __init__(self):
        self.service_type = IOPTServiceType.UNKNOWN
        self.keep_conn = False
        self.chunk_size = 0
        self.connection = None
        self.ip = None
        self.fn_parser_func = None
        self.SLAVE_LIBRARY = {}

    def set_connection(self, conn):
        self.connection = conn

    def set_ip(self, ip):
        self.ip = ip

    def initiate_connection(self, client_data):
        if self.fn_parser_func is None:
            return False
        if self.service_type is IOPTServiceType.BYTE:
            formated_req = self.fn_parser_func(client_data)
            # TODO Slave Validation :
            # slave id, number of digital operand
            # and number of analog operand
            # validate slave id uniqueness and range
            # otherwise reject the connection
            ret = self.fn_request_validate_byte(formated_req)
            if ret == 0:
                self.connection.send("200\n")
                return True
                # if everything goes fine, store slav information,
                #  send conformation  byte to slave, as the slave
                #  has been accepted
            elif ret == 1:
                self.connection.send("301\n")  # invalid request
                return False
            elif ret == -1:
                self.connection.send("300\n")  # invalid request
                return False
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
            self.fn_parser_func = self.fn_request_parser_byte_uci

        elif self.service_type is IOPTServiceType.IOTP:
            self.chunk_size = 128
            self.fn_parser_func = self.fn_request_parser_iotp_uci

        elif self.service_type is IOPTServiceType.HTTP:
            self.chunk_size = 128
            self.fn_parser_func = self.fn_request_parser_http_get

    @staticmethod
    def fn_request_parser_iotp_uci(request_uci):
        res = regex.match(
            r"^iotp://(?P<slv_id>s[0-9]+)((?P<slv_qer>\?)|(/(((?P<anlg_id>a[0-2])?((?P<anlg_qer>\?)|(/(?P<anlg_val>[0-9]{1,4}))))|((?P<digt_id>d[0-7])?((?P<digt_qer>\?)|(/(?P<digt_st>[01])))))))$",
            str(request_uci).lower(), regex.I | regex.M).groupdict()
        return res

    @staticmethod
    def fn_request_parser_http_get(request_info):
        request_url = ""
        res = regex.match(
            r"^http://(?P<slv_id>s[0-9]+)((?P<slv_qer>\?)|(/(((?P<anlg_id>a[0-2])?((?P<anlg_qer>\?)|(/(?P<anlg_val>[0-9]{1,4}))))|((?P<digt_id>d[0-7])?((?P<digt_qer>\?)|(/(?P<digt_st>[01])))))))$",
            str(request_url).lower(), regex.I | regex.M).groupdict()
        return res

    @staticmethod
    def fn_request_parser_byte_uci(request_uci):
        res = regex.match(
            r"^byte://(?P<slv_id>[0-9]+)/d/(?P<digt_ctr>[0-7])/a/(?P<anlg_ctr>[0-2])$",
            str(request_uci).lower(), regex.I | regex.M).groupdict()
        return res

    # validate a init request
    # return  0 OK
    # return  1 Duplicate Slave
    # return -1 Invalid Request
    def fn_request_validate_byte(self, formated_req):
        try:
            slave_id = int(formated_req[ByteRequestComponent.SLAVE_ID])
            if slave_id is not None and \
                    slave_id is not 0 and \
                    slave_id <= get_max_salve():
                if slave_id in self.SLAVE_LIBRARY:
                    _slave_info = self.SLAVE_LIBRARY[slave_id]
                    _slav_ip = _slave_info[0][0]
                    if str(_slav_ip) != str(self.ip[0]):
                        # duplicate slave id
                        return 1
                    else:
                        return 0
                else:
                    # new slave
                    self.SLAVE_LIBRARY[slave_id] = (self.ip,
                                                    int(formated_req[ByteRequestComponent.DIGITAL_COUNT]),
                                                    int(formated_req[ByteRequestComponent.ANALOG_COUNT]))
                    return 0


        except:
            return -1
