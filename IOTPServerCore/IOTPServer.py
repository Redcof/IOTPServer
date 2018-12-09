# Python program to implement server side of chat room.

import socket
from thread import *

from IOTPServerCore.IOTPRequest import IOPTServiceType

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
    def __init__(self, iotp_req, port=10700):  # 0 indicates any free port
        self.PORT = port
        self.HOST = "127.0.0.1"
        self.BACK_LOG = 20
        self.server = None
        self.list_of_iotp_slaves = []
        self.DEFAULT_BYTE_READ = 7
        self.req_handler_obj = iotp_req
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
            start_new_thread(self.client_thread, (conn, addr))

    def stop(self):
        if self.server is not None:
            for connection in self.list_of_iotp_slaves:
                connection.close()
                self.list_of_iotp_slaves.remove(connection)
            self.server.close()

    # handle client
    def client_thread(self, conn, addr):
        b_keep_loop = True
        # read client request line
        client_data = self.fn_client_read_line(conn)

        self.req_handler_obj.set_connection(conn)
        self.req_handler_obj.set_ip(addr)

        # check the Protocol as well as the type of the client
        if client_data.startswith(IOTProtocols.BYTE):
            self.req_handler_obj.set_type(IOPTServiceType.BYTE)
            self.list_of_iotp_slaves.append(conn)
        elif client_data.startswith(IOTProtocols.IOTP):
            self.req_handler_obj.set_type(IOPTServiceType.IOTP)
        elif client_data.startswith(IOTProtocols.HTTP):
            self.req_handler_obj.set_type(IOPTServiceType.HTTP)
        else:
            # invalid client
            conn.close()
            return

        # parse the request
        # initiate the connection for first time.
        b_keep_loop = self.req_handler_obj.initiate_connection(client_data)

        while b_keep_loop:
            b_keep_loop = self.req_handler_obj.keep_conn
            try:
                if formatted_data:
                    self.req_handler_obj.callback(formatted_data)
                    # reads new data
                    client_data = self.fn_client_read_line(conn)
                    formatted_data = self.req_handler_obj.fn_parser_func(client_data)
                else:
                    pass
                    # TODO Control Loop Break with INTERROGATION message
                    # message may have no content if the connection closed by client side
                    # self.remove(conn)
                    # break
            except:
                continue

        conn.close()
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
