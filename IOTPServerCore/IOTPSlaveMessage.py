_author_ = "int_soumen"
_date_ = "10-08-2018"

_TRANS_ID_ = 0x0000
_MAX_TRANS_ID_ = 0xFFFF


def fn_get_trans_id():
    global _TRANS_ID_, _MAX_TRANS_ID_
    _TRANS_ID_ += 1
    if _TRANS_ID_ > _MAX_TRANS_ID_:
        _TRANS_ID_ = 1
    return _TRANS_ID_


class IOTPSlaveMessage:

    def __init__(self):
        pass
        # self.RequestType = self.RequestType()
        # self.ResponseType = self.ResponseType()
        # self.MessageType = self.MessageType()

    class RequestType:
        def __init__(self):
            pass

        COMMAND = 0xC
        INTERROGATION = 0xE

    class ResponseType:
        def __init__(self):
            pass
            # self.StatusCode = self.StatusCode()

        ACKNOWLEDGEMENT = 0xA
        STATUS = 0xB

        class StatusCode:
            def __init__(self):
                pass

            SUCCESS = 200
            INVALID_REQUEST = 400
            OPERAND_NOT_FOUND = 404
            SYSTEM_ERROR = 500
            OPERAND_UNRESPONSIVE = 503

    class MessageType:
        def __init__(self):
            pass

        MESSAGE = 0xF
