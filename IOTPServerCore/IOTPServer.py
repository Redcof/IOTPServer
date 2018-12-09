# Python program to implement server side of chat room.
import copy
import json
import socket
from thread import *
import datetime
import time

from IOTPServerCore.IOTPCommon import SLAVE_LIBRARY, SERVER_JSON_CONF, PING_REPLY
from IOTPServerCore.IOTPRequest import IOPTServiceType, IOTPRequest
from IOTPServerCore.IOTPSlave import IOTPSlaveInfo
from IOTPServerCore.utils import log, void

##############################################
####### CHANGE GPIO MODE TO SIMULATION #######
##############################################
# from S4Hw.S4HwInterface import init_gpio, operate_gpio_digital, operate_gpio_analog, get_gpio_status
from S4Hw.dev_S4HwInterface import init_gpio, operate_gpio_digital, operate_gpio_analog, get_gpio_status
# LOG_PATH = '/home/pi/s4/iotp-serv-run.log'
LOG_PATH = '/Users/soumensardar/Downloads/iotp-serv-run.log'

_author_ = 'int_soumen'
_date_ = "27-07-2018"


class IOTProtocols:
    def __init__(self):
        pass

    BYTE = "byte://"  # byte://
    IOTP = "iotp://"  # iotp://s1/d1/1
    HTTP = "GET"  # GET /s5/d2/1 HTTP 1.1
    PING = "ping"  # GET /s5/d2/1 HTTP 1.1


# IOTP server wrapper
class IOTPServerCore():
    SIG_SLAVE_RESPONSE_RECEIVED = 0x00000001
    SIG_SLAVE_RESPONSE_TIMEOUT = 0x00000002

    # event_manager = IOTPEventManager((
    #     SIG_SLAVE_RESPONSE_RECEIVED,
    # ))

    def __init__(self, req_handler, server_home_dir, port=10700):  # 0 indicates any free port
        self.PORT = port
        self.HOST = ""
        self.BACK_LOG = 20
        self.server = None
        self.DEFAULT_BYTE_READ = 7
        self.RequestHandler = req_handler
        self.server_home = server_home_dir
        init_gpio([[3, 3, 3], [3, 3, 3]], 0)
        start_new_thread(self.blink, (1,))
        operate_gpio_digital(3, 1)
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
                    slave_dict = {"name": slave_json_obj['name'], 'id': slave_json_obj['id'],
                                  'image_uri': slave_json_obj['image_uri']}
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
        except KeyError, e:
            # clear all configuration as there is an error
            log(e)
            SLAVE_LIBRARY.clear()
            self.server_conf_status = False
        j_file.close()

    def start(self):
        global LOG_PATH
        operate_gpio_digital(3, 1)
        today = datetime.datetime.now()
        file_name = LOG_PATH
        # print file_name
        fr = open(file_name, 'a')
        fr.write('-=\n' + str(today) + '\n')
        fr.close()
        file = open(file_name, 'a')
        if self.server_conf_status is False:
            log("Configuration failed.")
            file.write("CONF FAIL.\n")
            file.close()
            return False
        if self.server is None:
            # configure the socket for start the IOTP server
            print "Wait for ETH port to be prepared..."
            time.sleep(30)
            print "ETH.OK"

            # bind socket with IP and PORT
            try:
                log("Server IP " + self.HOST)
                log("Server PORT " + str(self.PORT))
                file.write("...");
                file.close()
                file = open(file_name, 'a')
                while True:
                    try:
                        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.server.bind((self.HOST, self.PORT))
                        break
                    except socket.error, e:
                        print e
                        time.sleep(1)

                        # start listing to the incoming connection
                start_new_thread(self.s_listen, ())
                file.write('OK.RUNNING\n')
                file.close()
                operate_gpio_digital(3, 0)
                return True
            except socket.error, e:
                print e
                print "Unable to start server."
                file.write("PORT BLOCKED.\n")
                file.close()
                return False
        else:
            print "Socket bind failed."
            file.write("SOCKET FAIL.\n")
            file.close()
            return False

    def blink(self, closing_sts):
        operate_gpio_digital(3, 1)
        time.sleep(.1)
        operate_gpio_digital(3, 0)
        time.sleep(.1)
        operate_gpio_digital(3, 1)
        time.sleep(.1)
        operate_gpio_digital(3, 0)
        time.sleep(.1)
        operate_gpio_digital(3, 1)
        time.sleep(.1)
        operate_gpio_digital(3, 0)
        time.sleep(.1)
        operate_gpio_digital(3, closing_sts)

    def s_listen(self):
        # listen for new incoming connection
        self.server.listen(self.BACK_LOG)

        while True:
            # accept a new connection
            conn, addr = self.server.accept()

            # start a thread with client request
            start_new_thread(self.blink, (0,))
            start_new_thread(self.client_thread, (conn, addr, IOTPRequest()))

    def stop(self):
        if self.server is not None:
            for k in SLAVE_LIBRARY:
                k.socket.close()
            SLAVE_LIBRARY.clear()
            self.server.close()
            operate_gpio_digital(3, 1)

    # handle client in a thread
    def client_thread(self, incoming_conn, addr, request):
        initial_information = True
        # read client request line
        client_data = self.fn_client_read_line(incoming_conn)
        if client_data is None:
            incoming_conn.close()
            return

        print "Client connected {} with {} .".format(addr, client_data)
        request.set_connection(incoming_conn)
        request.set_ip(addr)

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
        elif client_data.startswith(IOTProtocols.PING):
            request.set_type(IOPTServiceType.PING)
            # http_service = True
            service_type_txt = "PING"
            print "Client{} Service Type: PING.".format(addr)
            self.handle_ping(incoming_conn, client_data)

        else:
            # invalid client
            incoming_conn.close()
            print "Invalid Client Closed. {}".format(addr)
            # return as not a valid client
            return

    # """ Keep connection and handle byte slave """
    # def hold_byte_slave(self, request, incoming_conn):
    #     formatted_data = True
    #     req_sts = request.keep_conn
    #
    #     while req_sts:
    #         try:
    #             if formatted_data:
    #                 # reads new data
    #                 client_data = self.fn_client_read_line(incoming_conn)
    #                 if client_data is None:
    #                     # slave offline
    #                     break
    #                 if client_data != "":
    #                     """ Signal Event as response has been received """
    #                     IOTPServerCore.event_manager.signal_event(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED,
    #                                                               client_data)
    #                     # TODO process client data if require
    #             else:
    #                 pass
    #                 # TODO Control Loop Break with INTERROGATION message
    #                 # message may have no content if the connection closed by client side
    #                 # self.remove(conn)
    #                 # break
    #         except RuntimeError, e:
    #             print e.message
    #             continue

    def handle_byte(self, request, slave_socket, slave_request, addr, service_type_txt):
        # validate and init connection with slave
        byte_request_uci = request.initiate_connection(slave_request)

        print "Client{} {} Request Status: {}.".format(addr, service_type_txt, byte_request_uci)

        """ Send reply to byte slave """
        try:
            slave_socket.send("[{},{}]\n".format(byte_request_uci[0], byte_request_uci[1]))
        except socket.error, e:
            log(e)
        except RuntimeError, e:
            print e.message

    def handle_iotp(self, iotp_request, app_socket, app_request, addr, service_type_txt):
        """initiate the connection for first time."""
        iotp_request_uci = iotp_request.initiate_connection(app_request)
        info = {}
        print "Client{} {} Request Status: {}.".format(addr, service_type_txt, iotp_request_uci)

        if iotp_request_uci[0] is 200:
            print "Client{} {} Request OK.".format(addr, service_type_txt)
            msg_frame = iotp_request.fn_prepare_slave_request()
            # print "Client{} {} Sending Command: {}".format(addr, msg_frame, service_type_txt)
            " Sending Request To IOTP Slave "
            try:
                slave_obj = SLAVE_LIBRARY[iotp_request.selected_slave_id]
                # send request to slave
                slave_obj.socket.send(msg_frame + "\n")
                # receive response from slave
                info = self.fn_client_read_line(slave_obj.socket)
                # # " waiting for slave to response "
                # IOTPServerCore.event_manager.event_wait(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED)
                # # clear the event
                # IOTPServerCore.event_manager.clear()
                # # get any extra data generate with this event,
                # i = IOTPServerCore.event_manager.get_event_extras()
                # info = i
            except:
                info = json.dumps({
                    'status_code': 503,
                    'status_text': 'Slave offline',
                    'message': 'Slave offline'
                })
        elif iotp_request_uci[0] is 201:
            info = json.dumps(iotp_request_uci[2])
        else:
            info = json.dumps({
                'status_code': iotp_request_uci[0],
                'message': iotp_request_uci[1]
            })

            """ Send reply to client """
        try:
            print "TX: {}\\n".format(info)
            app_socket.send("{}\n".format(info))
        except socket.error, e:
            log(e)
        try:
            app_socket.close()
        except:
            pass
        print "IOTP Client Closed: {}.".format(addr)

    def handle_http(self, request, incoming_conn, client_data, addr, service_type_txt):
        pass

    @staticmethod
    def handle_ping(incoming_conn, client_data):
        try:
            incoming_conn.send("{},{}\n".format(PING_REPLY, client_data))
            incoming_conn.close()
        except:
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
