from IntsUtil.util import log

_author_ = "int_soumen"
_date_ = "09-21-2018"


class IOTPSlaveInfo:
    def __init__(self, slave_id, do_list, ao_list, addr=("0.0.0.0", 0), socket=0):
        self.slave_id = slave_id
        self.address = addr
        self.socket = socket
        self.DO_Count = len(do_list)
        self.AO_Count = len(ao_list)
        self.DO_list = do_list
        self.AO_list = ao_list
        pass

    def close_connection(self):
        if self.socket is not 0:
            # close previous connection if any
            try:
                self.socket.close()
            except Exception, e:
                print  e
                pass
            log("{} Connection closed".format(self.address))
            self.socket = 0
            self.address = ("0.0.0.0", 0)

    def save(self, addr, sock):
        if self.socket is 0:
            self.address = addr
            self.socket = sock
        else:
            raise RuntimeError("Socket already available")

    def is_connected(self):
        return self.socket is not 0

    def check(self, operand):
        pass
