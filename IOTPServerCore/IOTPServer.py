# Python program to implement server side of chat room.
import copy
import json
import os
import socket
import time
from thread import *
import httplib, urllib

from IOTPServerCore.IOTPCommon import SLAVE_LIBRARY, SERVER_JSON_CONF, PING_REPLY, HTTP_BAD_REQUEST, HTTP_FORBIDDEN, \
    HTTP_NOT_FOUND, HTTP_UNAUTHORIZED, HTTP_SERVER_ERROR, HTTP_OK
from IOTPServerCore.IOTPRequest import IOPTServiceType, IOTPRequest
from IOTPServerCore.IOTPSlave import IOTPSlaveInfo
from IntsUtil.util import log, log_error
from S4Hw.S4Blink import S4LED

if os.path.exists("/home/pi"):
    from S4Hw.S4HwInterface import init_gpio, operate_gpio_digital

    CLOUD_HOST = "www.zodarica.com"
    URL_PREFIX = "/api"
    SLEEP_WAIT = 10
else:
    from S4Hw.dev_S4HwInterface import init_gpio, operate_gpio_digital

    # CLOUD_HOST = "localhost"
    # URL_PREFIX = "/zodarica/api"
    CLOUD_HOST = "www.zodarica.com"
    URL_PREFIX = "/api"
    SLEEP_WAIT = 1

OPR_WAIT_SEC = 1

_author_ = 'int_soumen'
_date_ = "27-07-2018"
_mod_ = "31-03-2019"


class IOTProtocols:
    def __init__(self):
        pass

    BYTE = "byte://"  # byte://
    IOTP = "iotp://"  # iotp://s1/d1/1
    HTTP = "HTTP"  # This is a spacial request fetched from Cloud Server
    PING = "ping://"  # GET /s5/d2/1 HTTP 1.1


# IOTP server wrapper
class IOTPServerCore():

    def __init__(self, req_handler, server_home_dir, port=10700):  # 0 indicates any free port
        global SLEEP_WAIT
        time.sleep(SLEEP_WAIT)
        self.PORT = port
        self.HOST = ""
        self.BACK_LOG = 20
        self.server = None
        self.DEFAULT_BYTE_READ = 7
        self.RequestHandler = req_handler
        self.server_home = server_home_dir
        self.StatusLED = S4LED(gpio=3)
        self.StatusLED.blink()
        self.server_conf_status = False
        self.init_server_conf()

        if self.server_conf_status:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect((SERVER_JSON_CONF['gateway'], 80))
                self.HOST = s.getsockname()[0]
            except socket.error, e:
                log_error(e.message)
            except KeyError, e:
                log_error(e.message)

    def init_server_conf(self):
        log("CONF IN PROGRESS...", False)
        try:
            json_path = self.server_home + '/iotp.json'
            log("Opening configuration JSON @ " + json_path, False)
            j_file = open(json_path)
            JSON = json.load(j_file, "ASCII")

            log(JSON)

            keys = ('copyright', 'date', 'author', 'name', 'master-id', 'id', 'username', 'password', 'gateway')
            for k in keys:
                SERVER_JSON_CONF[k] = copy.copy(JSON[k])

            slave_group_json_arr = JSON["slave-group"]
            if not isinstance(slave_group_json_arr, list):
                raise KeyError

            slave_group_list = []
            # Loop Each Slave Group
            debug_ctr1 = 0
            for group_json_obj in slave_group_json_arr:
                debug_ctr1 += 1
                log(debug_ctr1)
                group_dict = {"name": group_json_obj['name'], 'id': group_json_obj['id']}

                # get all slaves
                slave_json_arr = group_json_obj["slaves"]
                if not isinstance(slave_json_arr, list):
                    raise KeyError
                slave_list = []
                # Loop Each Slave
                debug_ctr2 = 0
                for slave_json_obj in slave_json_arr:
                    debug_ctr2 += 1
                    log(str(debug_ctr1) + "," + str(debug_ctr2))
                    slave_dict = {"name": slave_json_obj['name'], 'id': slave_json_obj['id'],
                                  'image_uri': slave_json_obj['image_uri']}
                    # get all operands
                    operand_json_arr = slave_json_obj["operands"]
                    if not isinstance(operand_json_arr, list):
                        raise KeyError
                    operand_list = []

                    do_list = []
                    ao_list = []
                    # Loop Each Slave Operand
                    debug_ctr3 = 0
                    for operand_json_obj in operand_json_arr:
                        debug_ctr3 += 1
                        log(str(debug_ctr1) + "," + str(debug_ctr2) + "," + str(debug_ctr3))
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
                # Slave count check
            SERVER_JSON_CONF['slave-group'] = slave_group_list
            self.server_conf_status = True
            j_file.close()
        except KeyError, e:
            # clear all configuration as there is an error
            log_error(e.message)
            SLAVE_LIBRARY.clear()
            self.server_conf_status = False

    def start(self):

        log("Try starting...", False)

        if self.server_conf_status is False:
            log("CONF FAIL.", False)
            return False
        if self.server is None:
            log("CONF OK.", False)
            # configure the socket for blink the IOTP server
            # bind socket with IP and PORT
            try:
                log("Server IP " + self.HOST)
                log("Server PORT " + str(self.PORT))
                log("Creating server...", False)
                while True:
                    try:
                        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        self.server.bind((self.HOST, self.PORT))
                        break
                    except socket.error, e:
                        print e
                        time.sleep(1)

                # blink listing to the incoming connection
                start_new_thread(self.socket_listener, ())

                log('SERVER OK.RUNNING.', False)

                self.StatusLED.stop_blink(0)

                """ START Thread FOR CLOUD SERVICE """
                start_new_thread(self.start_cloud_service, ())
                return True
            except socket.error, e:
                print e
                log("PORT BLOCKED")
                return False
        else:
            log("SOCKET FAIL.")
            return False

    def socket_listener(self):
        # listen for new incoming connection
        self.server.listen(self.BACK_LOG)

        while True:
            # accept a new connection
            conn, addr = self.server.accept()

            # blink a thread with client request
            start_new_thread(self.blink, (0,))
            start_new_thread(self.client_thread, (conn, addr, IOTPRequest()))

    def stop(self):
        if self.server is not None:
            # for k in SLAVE_LIBRARY:
            #     k.socket.close()
            SLAVE_LIBRARY.clear()
            self.server.close()
            self.StatusLED.blink()

    # handle client in a thread
    def client_thread(self, incoming_conn, addr, request):
        # read client request line
        client_data = self.fn_client_read_line(incoming_conn)
        if client_data is None:
            incoming_conn.close()
            return
        request.set_connection(incoming_conn)
        request.set_ip(addr)

        # check the Protocol as well as the type of the client
        if client_data.startswith(IOTProtocols.BYTE):
            request.set_type(IOPTServiceType.BYTE)
            # byte_service = True

            log("CLIENT [BYTE] IP:{} | REQUEST << {}".format(addr, client_data))

            self.handle_byte(request, incoming_conn, client_data, addr)
        elif client_data.startswith(IOTProtocols.IOTP):
            request.set_type(IOPTServiceType.IOTP)
            # iotp_service = True

            log("CLIENT [IOTP] IP:{} | REQUEST << {}".format(addr, client_data))

            self.handle_iotp(request, incoming_conn, client_data, addr)
        elif client_data.startswith(IOTProtocols.HTTP):
            # no use
            pass
        elif client_data.startswith(IOTProtocols.PING):
            request.set_type(IOPTServiceType.PING)
            # http_service = True

            log("CLIENT [PING] IP:{} | REQUEST << {}".format(addr, client_data))

            self.handle_ping(incoming_conn, addr, client_data)
        else:
            # invalid client
            incoming_conn.close()
            log("CLIENT CONNECTED [INVALID PROTOCOL] IP:{}".format(addr))
            return

    def handle_byte(self, request, slave_socket, slave_request, addr):
        # validate and init connection with slave
        byte_request_uci = request.initiate_connection(slave_request)

        """ Send reply to byte slave """
        try:
            response = "[{},{}]\n".format(byte_request_uci[0], byte_request_uci[1])
            slave_socket.send(response)
            log("CLIENT [BYTE] IP:{} | RESPONSE OK >> {}".format(addr, response))
        except socket.error, e:
            print e
            log("CLIENT [BYTE] IP:{} | RESPONSE ERROR - {}".format(addr, e.message))
        except RuntimeError, e:
            print e
            log("CLIENT [BYTE] IP:{} | RESPONSE ERROR - {}".format(addr, e.message))

    def handle_iotp(self, iotp_request, app_socket, app_data, addr):
        # comm. with slave
        response_json_string = self.comm_with_slave(iotp_request, app_data)
        try:
            log("CLIENT [IOTP] IP:{} | RESPONSE OK >> {}".format(addr, response_json_string))
            app_socket.send("{}\n".format(response_json_string))
        except socket.error, e:
            print e
            log("CLIENT [IOTP] IP:{} | RESPONSE ERROR - {}".format(addr, e.message))
        try:
            app_socket.close()
        except Exception, e:
            print e
            log_error(e.message)
            pass

    def handle_http(self, http_request, http_data):
        # comm. with slave
        response_json_string = self.comm_with_slave(http_request, http_data)
        return response_json_string
        pass

    def comm_with_slave(self, iotp_request, app_data):
        """ initiate the connection for first time. """
        iotp_request_uci = iotp_request.initiate_connection(app_data)
        """ communicate with stave """
        if iotp_request_uci[0] is 200:
            msg_frame = iotp_request.fn_prepare_slave_request()
            " Sending Request To IOTP Slave "
            try:
                slave_obj = SLAVE_LIBRARY[iotp_request.selected_slave_id]

                # send request to slave
                slave_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                slave_sock.setblocking(True)
                slave_sock.connect((slave_obj.address[0], 10701))
                slave_sock.sendall(msg_frame + "\n")

                log("CLIENT [IOTP] | REQUEST SLAVE IP:{} DATA >> {}".format(slave_obj.socket, msg_frame))

                info = self.fn_client_read_line(slave_sock)
                slave_sock.close()
                log("CLIENT [IOTP] | RESPONSE SLAVE IP:{} DATA << {}".format(slave_obj.socket, info))
            except Exception, e:
                print e
                info = json.dumps({
                    'status_code': 503,
                    'status_text': 'Slave offline',
                    'message': e.message
                })
        elif iotp_request_uci[0] is 201:
            info = json.dumps(iotp_request_uci[2])
        else:
            info = json.dumps({
                'status_code': iotp_request_uci[0],
                'message': iotp_request_uci[1]
            })
            """ Send reply to client """
        return info

    @staticmethod
    def handle_ping(incoming_conn, addr, client_data):
        try:
            incoming_conn.send("{},{}\n".format(PING_REPLY, client_data[7:]))
            log("CLIENT [PING] IP:{} | RESPONSE OK >> {},{}".format(addr, PING_REPLY, client_data[7:]))
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
                    except Exception, e:
                        """ Server offline """
                        string = None
                        break
                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except Exception, e:
                string = None
                break
        return string

    def blink(self, closing_sts):
        conf = self.StatusLED.get_conf()
        self.StatusLED.blink(mode="fast", retention="short")
        time.sleep(1)
        self.StatusLED.stop_blink(closing_sts)
        self.StatusLED.set_conf(conf)
        pass

    # TODO: Cloud Web Client
    def start_cloud_service(self):
        # step 1: login
        # step 2: if session available else login
        # step 3: read for command
        # step 4: execute command
        # step 5: if session available else login
        # step 6: write command status

        # step 1: login
        # Always send a "User-Agent": "IOTP" header in request
        # the username and password would be found in iotp.json file
        while True:
            try:
                log("Cloud Signing...")
                token = self.cloud_signing()
                if token is False:
                    log("oops! login failed.")
                    time.sleep(OPR_WAIT_SEC)
                    continue
                log("Login OK")

                log("Waiting for CMDs...")
                self.StatusLED.blink(mode="lazy", retention="tiny")
                while True:
                    # step 2: if session available else login
                    # step 3: read for command
                    cmd_list = self.read_pending_cloud_cmd(token)
                    if cmd_list == HTTP_UNAUTHORIZED:
                        log("oops! session expired.")
                        break
                    if cmd_list is not False:
                        self.blink(0)
                        # get the command count
                        command_count = len(cmd_list)
                        # get the latest command & ignore other commands
                        if command_count > 0:
                            # update command status to IN_EXE
                            for c in cmd_list:
                                log("Updating CMDs status to IN_EXE...")
                                try:
                                    params = urllib.urlencode(
                                        {'cmd_time': c['cmd_time'], 'status': 'IN_EXE'})
                                    headers = {
                                        "Content-type": "application/x-www-form-urlencoded",
                                        "Accept": "application/json",
                                        "User-Agent": "IOTP",
                                        "S4AUTH": token,
                                    }
                                    conn = httplib.HTTPConnection(CLOUD_HOST)
                                    conn.request("PUT", self.prepare_url("iotp-commands"), params, headers)
                                    response = conn.getresponse()
                                    # print response.read()
                                    pass
                                except Exception, e:
                                    pass
                            # get the last command
                            last_cmd = cmd_list[command_count - 1]
                            log("Executing CMD...")
                            req = IOTPRequest()
                            req.set_type(IOPTServiceType.HTTP)
                            response_json_string = self.handle_http(req, last_cmd['command'])
                            # update command status and value
                            log("Updating CMD to ACK_EXE...")
                            status = self.update_pending_cloud_cmd_status(last_cmd['cmd_time'], token,
                                                                          response_json_string)

                            if status == HTTP_UNAUTHORIZED:
                                log("oops! session expired.")
                                break
                    time.sleep(OPR_WAIT_SEC)
                    pass  # cmd fetch & exe loop
                self.StatusLED.stop_blink(0)
            except Exception, e:
                pass  # any exception
            time.sleep(OPR_WAIT_SEC)
        pass  # main login loop

    def prepare_url(self, route):
        return URL_PREFIX + "/" + route + "/"
        pass

    def cloud_signing(self):
        status = False
        conn = None
        try:
            params = urllib.urlencode(
                {'username': SERVER_JSON_CONF["username"], 'password': SERVER_JSON_CONF["password"]})
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "IOTP",
            }
            conn = httplib.HTTPConnection(CLOUD_HOST)
            conn.request("POST", self.prepare_url("login"), params, headers)
            response = conn.getresponse()
            data = response.read().decode('utf-8')

            if response.status == HTTP_OK:
                data = json.loads(data, 'utf-8')
                token = data['S4AUTH']
                status = token
                pass
            conn.close()
        except Exception, e:
            log_error(e.message)
            if conn is not None:
                conn.close()
            pass
        return status
        pass

    def read_pending_cloud_cmd(self, token):
        status = False
        conn = None
        try:
            # read a NEW command
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "IOTP",
                "S4AUTH": token,
            }
            conn = httplib.HTTPConnection(CLOUD_HOST)
            conn.request("GET", self.prepare_url("iotp-commands") + "?status=" + 'NEW', None, headers)
            response = conn.getresponse()
            cmd_list = response.read().decode('utf-8')
            # print cmd_list
            if response.status == HTTP_OK:
                # save the IOTP command string
                cmd_list = json.loads(cmd_list, 'utf-8')
                status = cmd_list
            elif response.status == HTTP_UNAUTHORIZED:
                status = HTTP_UNAUTHORIZED
            conn.close()
        except Exception, e:
            log_error(e.message)
            if conn is not None:
                conn.close()
            pass
        return status
        pass

    def update_pending_cloud_cmd_status(self, cmd_time, token, response_json_str):
        status = False
        conn = None
        try:
            params = urllib.urlencode(
                {'cmd_time': cmd_time, 'status': 'ACK_EXE', 'response': response_json_str})
            headers = {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": "IOTP",
                "S4AUTH": token,
            }
            conn = httplib.HTTPConnection(CLOUD_HOST)
            conn.request("PUT", self.prepare_url("iotp-commands"), params, headers)
            response = conn.getresponse()
            # saving http status
            status = response.status
            # print response.read()
            conn.close()
        except Exception, e:
            log_error(e.message)
            if conn is not None:
                conn.close()
            pass
        return status
        pass
