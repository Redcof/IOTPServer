import copy
import json
import re as regex

from IOTPServerCore.IOTPCommon import SERVER_JSON_CONF, SLAVE_LIBRARY
from IOTPServerCore.IOTPSecurity import IOTPSecureService, TOKEN, SIGN_IN
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
    PING = 4

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


class IOTPRequest:

    def __init__(self):
        self.service_type = IOPTServiceType.UNKNOWN
        self.keep_conn = False
        self.connection = None
        self.address = None
        self.selected_slave_id = None
        self.operand_id = None
        self.operand_cmd = None
        self.operand_type = None
        self.query_status = None

    def set_connection(self, conn):
        self.connection = conn

    def set_ip(self, addr):
        self.address = addr

    def initiate_connection(self, client_data):
        ret = (300, "Invalid request")
        tok = ""
        if self.service_type is IOPTServiceType.BYTE:
            # " BYTE Request Parsing "
            formatted_req = self.fn_slave_request_parser_byte_uci(client_data)
            # " Byte Request Validation "
            ret = self.fn_slave_request_validate_byte(formatted_req)
        elif self.service_type is IOPTServiceType.IOTP:
            # " IOTP Request Parsing "
            formatted_req = self.fn_master_request_parser_iotp_uci(client_data)
            if formatted_req['slv_qer'] is not None:
                self.query_status = True
            # "Request auth"
            auth = IOTPSecureService(
                SERVER_JSON_CONF["username"],
                SERVER_JSON_CONF["password"],
                formatted_req,
                IOPTServiceType.IOTP)
            # validate iotp request
            tok = auth.validate()

            if tok is not None:
                # " IOTP Request Validation "
                if auth.type is TOKEN:
                    ret = self.fn_master_request_validate_iotp(formatted_req)
                elif auth.type is SIGN_IN:
                    json_local = copy.deepcopy(SERVER_JSON_CONF)
                    # delete less important keys
                    del json_local['date']
                    del json_local['author']
                    del json_local['username']
                    del json_local['password']
                    del json_local['gateway']

                    json_local['token'] = tok
                    json_local['status_code'] = 200
                    ret = (201, "Sign In", json_local)
                    pass
            else:
                ret = (401, "Unauthorized access")
        elif self.service_type is IOPTServiceType.HTTP:
            pass

        return ret

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
            # self.fn_validator = self.fn_master_request_validate_iotp

        elif self.service_type is IOPTServiceType.HTTP:
            pass
            # self.chunk_size = 128
            # self.fn_parser = self.fn_request_parser_http_get

    @staticmethod
    def fn_master_request_parser_iotp_uci(request_uci):
        res = regex.match(
            r"^iotp://((?P<signin>sign/(?P<username>[^/]*)/(?P<password>[^/]*))|((tok/(?P<token>[0-9a-f]{32}))/(?P<slv_id>s[0-9]+)((?P<slv_qer>\?)|(/(((?P<anlg_id>a[1-7])?((?P<anlg_qer>\?)|(/(?P<anlg_val>[0-9]{1,4}))))|((?P<digt_id>d[1-7])?((?P<digt_qer>\?)|(/(?P<digt_st>[01])))))))))$",
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
    def fn_slave_request_parser_byte_uci(request_uci):
        res = regex.match(
            r"^byte://(?P<sid>[0-9]{1,2})/d:(?P<doc>[0-8])(?P<dol>\[(d[1-8](,d[1-8]){0,7}|)\])/a:(?P<aoc>[012])(?P<aol>\[(a[1-8](,a[1-8]){0,1}|)\])$",
            str(request_uci).lower(), regex.I | regex.M)
        if res:
            res = res.groupdict()
        return res

    """ validate a slave init reques"""

    # return  200 OK
    # return  300 Not found
    # return  503 Invalid Request
    def fn_slave_request_validate_byte(self, formatted_req):
        ret = (200, "OK")
        try:
            # get the slave id information
            slave_id = int(formatted_req[ByteRequestComponent.K_SLAVE_ID])
            self.selected_slave_id = slave_id

            # check availability and uniqueness
            # always accept the latest connection
            # previous connection should be closed
            # regardless of ip address
            if slave_id in SLAVE_LIBRARY:
                # get the slave info
                _slave_info = SLAVE_LIBRARY[slave_id]

                # check if connected, close the connection
                if _slave_info.is_connected():
                    _slave_info.close_connection()

                # set the address and connection socket
                _slave_info.set_socket(self.address, self.connection)
            else:
                # slave id not found
                ret = (300, "Invalid Request")
        except:
            ret = (503, "Server Error")
            pass
        return ret

    # validate a Master App request
    def fn_master_request_validate_iotp(self, formated_req):
        ret = (200, "OK")  # success
        # validate IOTP request mandatory fields
        while True:
            if formated_req is None:
                ret = (300, "Invalid Request")
                break

            slave_id = formated_req[IOTPRequestComponent.K_SLAVE_ID]
            if slave_id is None:
                ret = (300, "Invalid Request")  # Slave ID not provided # Invalid req
                break
            slave_id = int(slave_id[1:])
            if slave_id not in SLAVE_LIBRARY:
                ret = (404, "Slave not found")  # slave id dose not exists
                break

            self.selected_slave_id = slave_id

            # check digital operand status
            digi_opr_id = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_ID]
            if digi_opr_id is not None:
                do_list = SLAVE_LIBRARY[slave_id].DO_list
                if digi_opr_id not in do_list:
                    ret = (405, "Operand not found")  # digital operand dose not exists
                    break
                self.operand_id = digi_opr_id
                self.operand_cmd = int(formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS])
                self.query_status = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                self.operand_type = 0xD
                if self.operand_cmd is None and self.query_status is None:
                    # no query and no command
                    ret = (300, "Invalid Request")  # Invalid request
                    break

            # check analog operand status
            anlg_opr_id = formated_req[IOTPRequestComponent.K_ANALOG_OPERAND_ID]
            if anlg_opr_id is not None:
                ao_list = SLAVE_LIBRARY[slave_id].AO_list
                if anlg_opr_id not in ao_list:
                    ret = (405, "Operand not found")  # analog operand dose not exists
                    break
                self.operand_id = anlg_opr_id
                self.operand_cmd = int(formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_STATUS])
                self.query_status = formated_req[IOTPRequestComponent.K_DIGITAL_OPERAND_QUERY]
                self.operand_type = 0xA
                if self.operand_cmd is None and self.query_status is None:
                    # no query and no command
                    ret = (300, "Invalid Request")  # Invalid request
                    break

            if self.operand_cmd is not None:
                self.query_status = formated_req[IOTPRequestComponent.K_SLAVE_QUERY]
                if self.query_status is None and anlg_opr_id is None and digi_opr_id is None:
                    ret = (300, "Invalid Request")  # invalid request
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
    def fn_prepare_slave_request(self):
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
        else:
            # this is a interrogation
            header_frame = self.fn_create_slave_req_header(IOTPSlaveMessage.RequestType.INTERROGATION,
                                                           self.selected_slave_id)
            frame = header_frame + "{:01X}".format(0xD)
        return frame
