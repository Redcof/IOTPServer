# Python program to implement server side of chat room.
import copy
import json
import socket
from thread import *

from IOTPServerCore.IOTPCommon import SLAVE_LIBRARY, SERVER_JSON_CONF
from IOTPServerCore.IOTPEventManager import IOTPEventManager
from IOTPServerCore.IOTPRequest import IOPTServiceType, IOTPRequest
from IOTPServerCore.IOTPSlave import IOTPSlaveInfo
from IOTPServerCore.utils import log, void

_author_ = 'int_soumen'
_date_ = "27-07-2018"


class IOTProtocols:
    def __init__(self):
        pass

    BYTE = "byte://"  # byte://
    IOTP = "iotp://"  # iotp://s1/d1/1
    HTTP = "GET"  # GET /s5/d2/1 HTTP 1.1


# IOTP server wrapper
class IOTPServerCore():
    SIG_SLAVE_RESPONSE_RECEIVED = 0x00000001
    SIG_SLAVE_RESPONSE_TIMEOUT = 0x00000002

    event_manager = IOTPEventManager((
        SIG_SLAVE_RESPONSE_RECEIVED,
    ))

    def __init__(self, req_handler, server_home_dir, port=10700):  # 0 indicates any free port
        self.PORT = port
        self.HOST = "192.168.0.108"
        self.BACK_LOG = 20
        self.server = None
        self.DEFAULT_BYTE_READ = 7
        self.RequestHandler = req_handler
        self.server_home = server_home_dir

        self.server_conf_status = False
        self.init_server_conf()

        if self.server_conf_status:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((SERVER_JSON_CONF['gateway'], 80))
                self.HOST = s.getsockname()[0]
            except socket.error, e:
                log(e)
            except KeyError, e:
                log(e)

    def init_server_conf(self):
        dir_path = self.server_home
        j_file = open(dir_path + '/iotp.serverconf')
        JSON = json.load(j_file, "ASCII")
        try:
            keys = ('copyright', 'date', 'author', 'name', 'id', 'username', 'password', 'gateway')
            for k in keys:
                SERVER_JSON_CONF[k] = copy.copy(JSON[k])

            slave_group_json_arr = JSON["slave-group"]
            if not isinstance(slave_group_json_arr, list):
                raise KeyError

            slave_group_list = []
            # TODO: Loop Each Slave Group
            for group_json_obj in slave_group_json_arr:
                group_dict = {"name": group_json_obj['name'], 'id': group_json_obj['id']}

                # get all slaves
                slave_json_arr = group_json_obj["slaves"]
                if not isinstance(slave_json_arr, list):
                    raise KeyError
                slave_list = []
                # TODO: Loop Each Slave
                for slave_json_obj in slave_json_arr:
                    slave_dict = {"name": slave_json_obj['name'], 'id': slave_json_obj['id']}
                    # get all operands
                    operand_json_arr = slave_json_obj["operands"]
                    if not isinstance(operand_json_arr, list):
                        raise KeyError
                    operand_list = []

                    do_list = []
                    ao_list = []
                    # TODO: Loop Each Slave Operand
                    for operand_json_obj in operand_json_arr:
                        operand_dict = {"name": operand_json_obj['name'], 'id': operand_json_obj['id'],
                                        'state': operand_json_obj['state']}
                        operand_list.append(operand_dict)
                        if str(operand_json_obj["type"]) == 'd':
                            do_list.append("d{}".format(operand_json_obj["id"]))
                        if str(operand_json_obj["type"]) == 'a':
                            ao_list.append("a{}".format(operand_json_obj["id"]))

                    slave_dict['operands'] = operand_list
                    slave_list.append(slave_dict)
                    # save th slave configuration
                    SLAVE_LIBRARY[int(slave_json_obj["id"])] = IOTPSlaveInfo(int(slave_json_obj["id"]), do_list,
                                                                             ao_list)
                group_dict['slaves'] = slave_list
                slave_group_list.append(group_dict)

                # TODO Slave count check

            SERVER_JSON_CONF['slave-group'] = slave_group_list

            self.server_conf_status = True

            print SERVER_JSON_CONF
        except KeyError, e:
            # clear all configuration as there is an error
            log(e)
            SLAVE_LIBRARY.clear()
            self.server_conf_status = False
        j_file.close()

    def start(self):
        if self.server_conf_status is False:
            log("Configuration failed.")
            return False
        if self.server is None:
            # configure the socket for start the IOTP server
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # bind socket with IP and PORT
            try:
                log("Server IP " + self.HOST)
                log("Server PORT " + str(self.PORT))
                self.server.bind((self.HOST, self.PORT))
                # start listing to the incoming connection
                start_new_thread(self.s_listen, ())
                return True
            except socket.error, e:
                print e
                print "Unable to start server."
                return False

    def s_listen(self):
        # listen for new incoming connection
        self.server.listen(self.BACK_LOG)

        while True:
            # accept a new connection
            conn, addr = self.server.accept()

            # start a thread with client request
            start_new_thread(self.client_thread, (conn, addr, IOTPRequest()))

    def stop(self):
        if self.server is not None:
            for k in SLAVE_LIBRARY:
                k.socket.close()
            SLAVE_LIBRARY.clear()
            self.server.close()

    # handle client in a thread
    def client_thread(self, incoming_conn, addr, request):
        initial_information = True
        # read client request line
        client_data = self.fn_client_read_line(incoming_conn)

        print "Client {} connected.".format(addr)
        request.set_connection(incoming_conn)
        request.set_ip(addr)

        # byte_service = False
        # iotp_service = False
        # http_service = False

        # service_type_txt = ""

        # check the Protocol as well as the type of the client
        if client_data.startswith(IOTProtocols.BYTE):
            request.set_type(IOPTServiceType.BYTE)
            # byte_service = True
            service_type_txt = "IOTP Slave"
            log("Client{} Service Type: IOTP Slave.".format(addr))
            self.handle_byte(request, incoming_conn, client_data, addr, service_type_txt)

        elif client_data.startswith(IOTProtocols.IOTP):
            request.set_type(IOPTServiceType.IOTP)
            # iotp_service = True
            service_type_txt = "IOTP Master"
            print "Client{} Service Type: IOTP Master.".format(addr)
            self.handle_iotp(request, incoming_conn, client_data, addr, service_type_txt)

        elif client_data.startswith(IOTProtocols.HTTP):
            request.set_type(IOPTServiceType.HTTP)
            # http_service = True
            service_type_txt = "HTTP"
            print "Client{} Service Type: HTTP.".format(addr)
            self.handle_http(request, incoming_conn, client_data, addr, service_type_txt)
        else:
            # invalid client
            incoming_conn.close()
            print "Invalid Client Closed. {}".format(addr)
            # return as not a valid client
            return

    """ Keep connection and handle byte slave """

    def hold_byte_slave(self, request, incoming_conn):
        formatted_data = True
        req_sts = request.keep_conn

        while req_sts:
            try:
                if formatted_data:
                    # reads new data
                    client_data = self.fn_client_read_line(incoming_conn)
                    if client_data is None:
                        # slave offline
                        break
                    if client_data != "":
                        """ Signal Event as response has been received """
                        IOTPServerCore.event_manager.signal_event(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED,
                                                                  client_data)
                        # TODO process client data if require
                else:
                    pass
                    # TODO Control Loop Break with INTERROGATION message
                    # message may have no content if the connection closed by client side
                    # self.remove(conn)
                    # break
            except:
                continue

    def handle_byte(self, request, incoming_conn, client_data, addr, service_type_txt):
        # validate and init connection with slave
        _init_info = request.initiate_connection(client_data)

        print "Client{} {} Request Status: {}.".format(addr, service_type_txt, _init_info)

        """ Send reply to byte slave """
        try:
            incoming_conn.send("[{},{}]\n".format(_init_info[0], _init_info[1]))
        except socket.error, e:
            log(e)
            return

        """ Handle Byte Slaves """
        if _init_info[0] is 200:
            pass
            self.hold_byte_slave(request, incoming_conn)
        try:
            incoming_conn.close()
        except:
            pass
        print "Byte Slave Closed: {}.".format(addr)

    @staticmethod
    def handle_iotp(request, incoming_conn, client_data, addr, service_type_txt):
        """initiate the connection for first time."""
        _init_info = request.initiate_connection(client_data)
        info = ""
        print "Client{} {} Request Status: {}.".format(addr, service_type_txt, _init_info)

        if _init_info[0] is 200:
            print "Client{} {} Request OK.".format(addr, service_type_txt)
            msg_frame = request.fn_prepare_slave_request()
            # print "Client{} {} Sending Command: {}".format(addr, msg_frame, service_type_txt)
            " Sending Request To IOTP Slave "
            try:
                SLAVE_LIBRARY[request.selected_slave_id].socket.send(msg_frame + "\n")
                # " waiting for slave to response "
                IOTPServerCore.event_manager.event_wait(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED)
                # clear the event
                IOTPServerCore.event_manager.clear()
                # get any extra data generate with this event,
                info = IOTPServerCore.event_manager.get_event_extras()
            except:
                info = (503, "Slave offline")
        elif _init_info[0] is 201:
            info = json.dumps(_init_info[2])
        else:
            info = _init_info

        """ Send reply to client """
        try:
            incoming_conn.send("{}\n".format(info))
        except socket.error, e:
            log(e)
        try:
            incoming_conn.close()
        except:
            pass
        print "IOTP Client Closed: {}.".format(addr)

    def handle_http(self, request, incoming_conn, client_data, addr, service_type_txt):
        pass

    @staticmethod
    def fn_client_read_line(conn):
        string = ""
        while True:
            try:
                d = str(conn.recv(1))
                if len(d) is 0:
                    try:
                        """ Trying with a CR to check connection """
                        conn.sendall("\n")
                    except:
                        """ Server offline """
                        string = None
                        break
                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except:
                string = None
                break
        return string
