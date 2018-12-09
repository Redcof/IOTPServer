# Python program to implement server side of chat room.

import socket
from thread import *

from IOTPServerCore.IOTPEventManager import IOTPEventManager
from IOTPServerCore.IOTPRequest import IOPTServiceType, IOTPRequest

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

    def __init__(self, req_handler, port=10700):  # 0 indicates any free port
        self.PORT = port
        self.HOST = "127.0.0.1"
        self.BACK_LOG = 20
        self.server = None
        self.list_of_iotp_slaves = {}
        self.DEFAULT_BYTE_READ = 7
        self.RequestHandler = req_handler
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        self.HOST = s.getsockname()[0]

    def start(self):
        if self.server is None:
            # configure the socket for start the IOTP server
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # bind socket with IP and PORT
            try:
                print "Server IP " + self.HOST
                print "Server PORT " + str(self.PORT)
                self.server.bind((self.HOST, self.PORT))
                # start listing to the incoming connection
                start_new_thread(self.s_listen, ())
                return True
            except Exception, e:
                print e.message
                print "Unable to start server."
                return False

    def s_listen(self):
        # listen for new incoming connection
        self.server.listen(self.BACK_LOG)

        while True:
            # accept a new connection
            conn, addr = self.server.accept()

            # prints the address of the user that just connected
            # print addr[0] + " connected"

            # creates and individual thread for every user

            start_new_thread(self.client_thread, (conn, addr, IOTPRequest()))

    def stop(self):
        if self.server is not None:
            for k in self.list_of_iotp_slaves:
                self.list_of_iotp_slaves[k].close()
                del self.list_of_iotp_slaves[k]
            self.server.close()

    # handle client
    def client_thread(self, conn, addr, request):
        req_sts = True
        # read client request line
        client_data = self.fn_client_read_line(conn)
        print "Client {} connected.".format(addr)

        request.set_connection(conn)
        request.set_ip(addr)

        byte_service = False
        iotp_service = False
        http_service = False

        service_type = ""

        # check the Protocol as well as the type of the client
        if client_data.startswith(IOTProtocols.BYTE):
            request.set_type(IOPTServiceType.BYTE)
            byte_service = True
            service_type = "IOTP Slave"
            print "Client{} Service Type: IOTP Slave.".format(addr)
        elif client_data.startswith(IOTProtocols.IOTP):
            request.set_type(IOPTServiceType.IOTP)
            iotp_service = True
            service_type = "IOTP Master"
            print "Client{} Service Type: IOTP Master.".format(addr)
        elif client_data.startswith(IOTProtocols.HTTP):
            request.set_type(IOPTServiceType.HTTP)
            http_service = True
            service_type = "HTTP"
            print "Client{} Service Type: HTTP.".format(addr)
        else:
            # invalid client
            conn.close()
            print "Client {} {} Closed.".format(addr, service_type)
            return

        # parse the request
        # initiate the connection for first time.
        req_sts = request.initiate_connection(client_data)

        if req_sts is 200:
            print "Client{} {} Request OK.".format(addr, service_type)
            if iotp_service is True:
                msg_frame = request.fn_prepare_slave_request(request.formatted_req)
                print "Client{} {} Sending Command: {}".format(addr, msg_frame, service_type)
                " Sending Request To IOTP Slave "
                self.list_of_iotp_slaves[request.selected_slave_id].send(msg_frame+"\n")
                " waiting for slave to response"
                IOTPServerCore.event_manager.event_wait(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED)
                info = IOTPServerCore.event_manager.get_event_extras()
                " Send Response to IOTP Master App "
                conn.send("200\n")
                IOTPServerCore.event_manager.clear()
            if byte_service is True:
                self.list_of_iotp_slaves[request.selected_slave_id] = conn
                conn.send("200\n")
        else:
            conn.send("{}\n".format(req_sts))

        print "Client{} {} Request Status: {}.".format(addr,service_type, req_sts)
        formatted_data = True

        while req_sts:
            req_sts = request.keep_conn
            try:
                if formatted_data:
                    # request.callback(formatted_data)
                    # reads new data
                    client_data = self.fn_client_read_line(conn)
                    if client_data != "":
                        IOTPServerCore.event_manager.signal_event(IOTPServerCore.SIG_SLAVE_RESPONSE_RECEIVED, client_data)
                        # formatted_data = request.fn_parser_func(client_data)
                        # self.RequestHandler.callback(request, formatted_data)
                else:
                    pass
                    # TODO Control Loop Break with INTERROGATION message
                    # message may have no content if the connection closed by client side
                    # self.remove(conn)
                    # break
            except:
                continue

        conn.close()
        print "Client {} {} Closed.".format(addr, service_type)

    # print addr[0] + "Closed."

    # The following function simply removes the object
    # from the list that was created at the beginning of
    # the program

    def remove(self, connection):
        if connection in self.list_of_iotp_slaves:
            self.list_of_iotp_slaves.remove(connection)

    @staticmethod
    def fn_client_read_line(conn):
        string = ""
        while True:
            try:
                d = str(conn.recv(1))
                if d == "\n" or d == "\r":
                    break
                string += d
                continue
            except:
                break
        return string
