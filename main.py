import os
import time
import IOTP_CommandLine.commands as cmd
from IntsUtil import util
from IntsUtil.util import log

_author_ = "int_soumen"
_date_ = "2019-JAN-03"

if __name__ == "__main__":
    _version_ = "2.0.0"
    print "Welcome to IOTP server version " + _version_

    server_home = util.home_dir
    try:
        if cmd.iotp_start(server_home):
            while True:
                time.sleep(10000)
                pass
    except KeyboardInterrupt, e:
        cmd.iptp_stop()
        pass
    log("EXIT.")
