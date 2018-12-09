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

    K_SLAVE_ID = "slv_id"
    K_SLAVE_QUERY = "slv_qer"
    K_DIGITAL_OPERAND_ID = "digt_id"
    K_DIGITAL_OPERAND_QUERY = "digt_qer"
    K_DIGITAL_OPERAND_STATUS = "digt_st"
    K_ANALOG_OPERAND_ID = "anlg_id"
    K_ANALOG_OPERAND_QUERY = "anlg_qer"
    K_ANALOG_OPERAND_VALUE = "anlg_val"


class ByteRequestComponent:
    def __init__(self):
        pass

    K_SLAVE_ID = "sid"
    K_DIGITAL_COUNT = "doc"
    K_DIGITAL_LIST = "dol"
    K_ANALOG_COUNT = "aoc"
    K_ANALOG_LIST = "aol"


def get_max_salve():
    return 25


class IOTPRequest:

    def __init__(self):
        self.service_type = IOPTServiceType.UNKNOWN
        self.keep_conn = False
        self.chunk_size = 0
        self.connection = None
        self.ip = None
        # self.fn_parser = None
        # self.fn_validator = None
        self.SLAVE_LIBRARY = {}

    def set_connection(self, conn):
        self.connection = conn

    def set_ip(self, ip):
        self.ip = ip

    def initiate_connection(self, client_data):
        if self.service_type is IOPTServiceType.BYTE:
            # TODO Slave Validation :
            # slave id, number of digital operand
            # and number of analog operand
            # validate slave id uniqueness and range
            # otherwise reject the connection
            "parse the request"
            formatted_req = self.fn_request_parser_byte_uci(client_data)
            "validate request"
            ret = self.fn_request_validate_byte(formatted_req)
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
            " OTP Request Parsing "
            formatted_req = self.fn_request_parser_iotp_uci(client_data)
            " TODO IOTP Request Validation "
            ret = self.fn_request_validate_iotp(formatted_req)

            self.connection.send(str(ret) + "\n")
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
            # self.fn_parser = self.fn_request_parser_byte_uci
            # self.fn_validator = self.fn_request_validate_byte

        elif self.service_type is IOPTServiceType.IOTP:
            self.chunk_size = 128
            # self.fn_parser = self.fn_request_parser_iotp_uci
            # self.fn_validator = self.fn_request_validate_iotp

        elif self.service_type is IOPTServiceType.HTTP:
            self.chunk_size = 128
            # self.fn_parser = self.fn_request_parser_http_get

    @staticmethod
    def fn_request_parser_iotp_uci(request_uci):
        res = regex.match(
            r"^iotp://(?P<slv_id>s[0-9]+)((?P<slv_qer>\?)|(/(((?P<anlg_id>a[0-2])?((?P<anlg_qer>\?)|(/(?P<anlg_val>[0-9]{1,4}))))|((?P<digt_id>d[0-7])?((?P<digt_qer>\?)|(/(?P<digt_st>[01])))))))$",
            str(request_uci).lower(), regex.I | regex.M)
        if res:
            res = res.groupdict()
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
            r"^byte://(?P<sid>[0-9]{1,2})/d:(?P<doc>[0-8])(?P<dol>\[(d[1-8](,d[1-8]){0,7}|)\])/a:(?P<aoc>[012])(?P<aol>\[(a[1-8](,a[1-8]){0,1}|)\])$",
            str(request_uci).lower(), regex.I | regex.M)
        if res:
            res = res.groupdict()
        return res

    # validate a slave init request
    # return  0 OK
    # return  1 Duplicate Slave
    # return -1 Invalid Request
    def fn_request_validate_byte(self, formated_req):
        ret = 0
        try:
            # get the slave id information
            slave_id = int(formated_req[ByteRequestComponent.K_SLAVE_ID])
            # check limits
            if slave_id is not None and \
                    slave_id is not 0 and \
                    slave_id <= get_max_salve():
                # check uniqueness
                if slave_id in self.SLAVE_LIBRARY:
                    _slave_info = self.SLAVE_LIBRARY[slave_id]
                    _slav_ip = _slave_info[0][0]
                    # check IP address
                    if str(_slav_ip) != str(self.ip[0]):
                        # duplicate slave id
                        ret = 1
                else:
                    # new slave
                    dol = formated_req[ByteRequestComponent.K_DIGITAL_LIST].replace('[', '').replace(']', '').split(',')
                    aol = formated_req[ByteRequestComponent.K_ANALOG_LIST].replace('[', '').replace(']', '').split(',')
                    self.SLAVE_LIBRARY[int(slave_id)] = (self.ip,
                                                         int(formated_req[ByteRequestComponent.K_DIGITAL_COUNT]),
                                                         int(formated_req[ByteRequestComponent.K_ANALOG_COUNT]),
                                                         dol,
                                                         aol)
        except:
            ret = -1
        return ret

    # validate a Master App request
    def fn_request_validate_iotp(self, formated_req):
        ret = 200  # success
        # validate IOTP request mandatory fields
        while True:
            if formated_req is None:
                ret = 300
                break

            slave_id = formated_req[IOTPRequestComponent.K_SLAVE_ID]
            if slave_id is None:
                ret = 300  # Slave ID not provided # Invalid req
                break
            slave_id = int(slave_id.lstrip('s'))
            if slave_id not in self.SLAVE_LIBRARY:
                ret = 404  # slave id dose not exists
                break

            # check digital operand status
            digi_opr_id = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_ID]
            if digi_opr_id is not None:
                if digi_opr_id not in self.SLAVE_LIBRARY[slave_id][3]:
                    ret = 405  # digital operand dose not exists
                    break
                opr_cmd = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS]
                opr_qry = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                if opr_cmd is None and opr_qry is None:
                    # no query and no command
                    ret = 300  # Invalid request
                    break

            # check analog operand status
            anlg_opr_id = formated_req[IOTPRequestComponent.K_ANALOG_OPERAND_ID]
            if anlg_opr_id is not None:
                if anlg_opr_id not in self.SLAVE_LIBRARY[slave_id][4]:
                    ret = 405  # analog operand dose not exists
                    break
                opr_cmd = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS]
                opr_qry = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                if opr_cmd is None and opr_qry is None:
                    # no query and no command
                    ret = 300  # Invalid request
                    break

            slave_qry = formated_req[IOTPRequestComponent.K_SLAVE_QUERY]
            if slave_qry is None and anlg_opr_id is None and digi_opr_id is None:
                ret = 300  # invalid request
                break

            break  # while loop break
        return ret
