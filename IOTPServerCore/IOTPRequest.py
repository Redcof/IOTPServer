import re as regex

from IOTPServerCore.IOTPSlaveMessage import fn_get_trans_id, IOTPSlaveMessage

__author_ = "int_soumen"
_date_ = "29-07-2018"


class IOPTServiceType:
    def __init__(self):
        pass

    UNKNOWN = 0
    BYTE = 1
    IOTP = 2
    HTTP = 3

    class Validation:
        def __init__(self):
            pass

        SUCCESS = 200


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


BYTE_SLAVE_LIBRARY = {}


class IOTPRequest:

    def __init__(self):
        self.service_type = IOPTServiceType.UNKNOWN
        self.keep_conn = False
        self.connection = None
        self.ip = None
        self.selected_slave_id = None
        self.operand_id = None
        self.operand_cmd = None
        self.operand_type = None
        self.query_status = None

    def set_connection(self, conn):
        self.connection = conn

    def set_ip(self, ip):
        self.ip = ip

    def initiate_connection(self, client_data):
        if self.service_type is IOPTServiceType.BYTE:
            " BYTE Request Parsing "
            formatted_req = self.fn_request_parser_byte_uci(client_data)
            " Byte Request Validation "
            ret = self.fn_request_validate_byte(formatted_req)
            return ret
        elif self.service_type is IOPTServiceType.IOTP:
            " IOTP Request Parsing "
            self.formatted_req = self.fn_request_parser_iotp_uci(client_data)
            " TODO IOTP Request Validation "
            ret = self.fn_request_validate_iotp(self.formatted_req)
            return ret

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
            # self.chunk_size = 64
            # self.fn_parser = self.fn_request_parser_byte_uci
            # self.fn_validator = self.fn_request_validate_byte

        elif self.service_type is IOPTServiceType.IOTP:
            pass
            # self.chunk_size = 128
            # self.fn_parser = self.fn_request_parser_iotp_uci
            # self.fn_validator = self.fn_request_validate_iotp

        elif self.service_type is IOPTServiceType.HTTP:
            pass
            # self.chunk_size = 128
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
        ret = 200
        try:
            # get the slave id information
            slave_id = int(formated_req[ByteRequestComponent.K_SLAVE_ID])
            self.selected_slave_id = slave_id
            # check limits
            if slave_id is not None and \
                    slave_id is not 0 and \
                    slave_id <= get_max_salve():
                # check uniqueness
                if slave_id in BYTE_SLAVE_LIBRARY:
                    _slave_info = BYTE_SLAVE_LIBRARY[slave_id]
                    _slav_ip = _slave_info[0][0]
                    # check IP address
                    if str(_slav_ip) != str(self.ip[0]):
                        # duplicate slave id
                        ret = 300
                else:
                    # new slave
                    dol = formated_req[ByteRequestComponent.K_DIGITAL_LIST].replace('[', '').replace(']', '').split(',')
                    aol = formated_req[ByteRequestComponent.K_ANALOG_LIST].replace('[', '').replace(']', '').split(',')
                    BYTE_SLAVE_LIBRARY[int(slave_id)] = (self.ip,
                                                         int(formated_req[ByteRequestComponent.K_DIGITAL_COUNT]),
                                                         int(formated_req[ByteRequestComponent.K_ANALOG_COUNT]),
                                                         dol,
                                                         aol)
        except:
            ret = 503
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
            slave_id = int(slave_id[1:])
            if slave_id not in BYTE_SLAVE_LIBRARY:
                ret = 404  # slave id dose not exists
                break

            self.selected_slave_id = slave_id

            # check digital operand status
            digi_opr_id = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_ID]
            if digi_opr_id is not None:
                if digi_opr_id not in BYTE_SLAVE_LIBRARY[slave_id][3]:
                    ret = 405  # digital operand dose not exists
                    break
                self.operand_id = digi_opr_id
                self.operand_cmd = int(formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS])
                self.query_status = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                self.operand_type = 0xD
                if self.operand_cmd is None and self.query_status is None:
                    # no query and no command
                    ret = 300  # Invalid request
                    break

            # check analog operand status
            anlg_opr_id = formated_req[IOTPRequestComponent.K_ANALOG_OPERAND_ID]
            if anlg_opr_id is not None:
                if anlg_opr_id not in BYTE_SLAVE_LIBRARY[slave_id][4]:
                    ret = 405  # analog operand dose not exists
                    break
                self.operand_id = anlg_opr_id
                self.operand_cmd = int(formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS])
                self.query_status = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                self.operand_type = 0xA
                if self.operand_cmd is None and self.query_status is None:
                    # no query and no command
                    ret = 300  # Invalid request
                    break

            if self.operand_cmd is not None:
                self.query_status = formated_req[IOTPRequestComponent.K_SLAVE_QUERY]
                if self.query_status is None and anlg_opr_id is None and digi_opr_id is None:
                    ret = 300  # invalid request
                    break

            break  # while loop break
        return ret

    @staticmethod
    def fn_create_slave_req_header(transaction_type_id, slave_id):
        frame = "{:01X}{:04X}{:04X}".format(transaction_type_id,
                                            fn_get_trans_id(),
                                            slave_id
                                            )
        return frame

    # function to prepare IOTP Slave Request
    def fn_prepare_slave_request(self, formatted_req):
        if self.query_status is None:
            # this is a command
            header_frame = self.fn_create_slave_req_header(IOTPSlaveMessage.RequestType.COMMAND,
                                                           self.selected_slave_id)
            no_opr = 1
            frame = header_frame + "{:01X}{:01X}{:01X}{:04X}".format(no_opr,
                                                                     self.operand_type,
                                                                     int(self.operand_id[1:]),
                                                                     self.operand_cmd
                                                                     )
            return frame
