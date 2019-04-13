import os
import time
import IOTP_CommandLine.commands as cmd
from IntsUtil import util
from IntsUtil.util import log

_author_ = "int_soumen"
_date_ = "2019-JAN-03"

if __name__ == "__main__":
    _version_ = "2.5.11"
    log("Welcome to IOTP server version " + _version_, False)

    try:
        if cmd.iotp_start(util.HOME_DIR):
            while True:
                time.sleep(10000)
                pass
    except KeyboardInterrupt, e:
        cmd.iptp_stop()
        pass
    log("EXIT.", False)
