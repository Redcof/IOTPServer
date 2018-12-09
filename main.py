import os
import time
import IOTP_CommandLine.commands as cmd
from IOTPServerCore.utils import log

_author_ = "int_soumen"
_date_ = "2018-09-17"

if __name__ == "__main__":
    _version_ = "1.0.0"
    print "Welcome to IOTP server version " + _version_

    server_home = os.path.dirname(os.path.realpath(__file__))

    if cmd.iotp_start(server_home):
        while True:
            time.sleep(1)
            pass

    log("END")
