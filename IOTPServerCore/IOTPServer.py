# Python program to implement server side of chat room.
from IOTPServerCore.IOTPRequest import IOPTServiceType

_author_ = 'int_soumen'
_date_ = "27-07-2018"

import socket
import re as regex
from thread import *


class IOTProtocols:
    def __init__(self):
        pass

    BYTE = "byte://"  # byte://
    IOTP = "iotp://"  # iotp://s1/d1/1
    HTTP = "GET"  # GET /s5/d2/1 HTTP 1.1


# IOTP server wrapper
class IOTPServerCore():
    def __init__(self, iotp_req, port = 10700):  # 0 indicates any free port
        self.PORT = port
        self.HOST = "127.0.0.1"
        self.BACK_LOG = 20
        self.server = None
        self.list_of_clients = []
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

            # list up the connection information
            self.list_of_clients.append(conn)

            # prints the address of the user that just connected
            # print addr[0] + " connected"

            # creates and individual thread for every user
            start_new_thread(self.client_thread, (conn, addr))

    def stop(self):
        if self.server is not None:
            for connection in self.list_of_clients:
                connection.close()
                self.list_of_clients.remove(connection)
            self.server.close()

    def client_thread(self, conn, addr):
        b_keep_loop = True
        # sends a message to the client whose user object is conn
        request = self.client_read_line(conn)
        formatted_data = True  # let the calback to be called

        if request.startswith(IOTProtocols.BYTE):
            self.req_handler_obj.set_type(IOPTServiceType.BYTE)
            formatted_data = True  # let the calback to be called
        elif request.startswith(IOTProtocols.IOTP):
            self.req_handler_obj.set_type(IOPTServiceType.IOTP)
            formatted_data = self.request_parser_iotp_uci(request)
        elif request.startswith(IOTProtocols.HTTP):
            self.req_handler_obj.set_type(IOPTServiceType.HTTP)

        while b_keep_loop:
            b_keep_loop = self.req_handler_obj.keep_conn
            try:
                if formatted_data:
                    self.req_handler_obj.callback(conn, addr, formatted_data)
                    formatted_data = conn.recv(self.req_handler_obj.chunk_size)
                else:
                    # message may have no content if the connection
                    #     is broken, in this case we remove the connection"""
                    self.remove(conn)
                    break
            except:
                continue
        # print addr[0] + "Closed."

    # """Using the below function, we broadcast the message to all
    # clients who's object is not the same as the one sending
    # the message """

    def broadcast(self, message, connection):
        for clients in self.list_of_clients:
            if clients != connection:
                try:
                    clients.send(message)
                except:
                    clients.close()

                    # if the link is broken, we remove the client
                    self.remove(clients)

    # """The following function simply removes the object
    # from the list that was created at the beginning of
    # the program"""

    def remove(self, connection):
        if connection in self.list_of_clients:
            self.list_of_clients.remove(connection)

    def client_read_line(self, conn):
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

    def request_parser_iotp_uci(self, request_UCI):
        res = regex.match(
            r"iotp://(?P<slv_id>s[0-9]+)((?P<slv_qer>\?)|(/(((?P<anlg_id>a[0-2])?((?P<anlg_qer>\?)|(/(?P<anlg_val>[0-9]{1,4}))))|((?P<digt_id>d[0-7])?((?P<digt_qer>\?)|(/(?P<digt_st>[01])))))))",
            str(request_UCI).lower(), regex.I | regex.M).groupdict()
        return res
