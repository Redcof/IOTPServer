from S4Crypto.S4Hash import s4hash

_author_ = "int_soumen"
_date_ = "09-17-2018"

SIGN_IN = 1
TOKEN = 2


class IOTPSecureService:

    def __init__(self, conf_username, conf_password, formatted_req, service_type):
        self.formatted_req = formatted_req
        self.service_type = service_type
        self.conf_username_h = conf_username
        self.conf_password_h = conf_password
        self.type = 0
        pass

    def validate(self):
        status = False
        token_h = None
        while True:
            # if request is null; validation failed
            if self.formatted_req is None:
                break

            from IOTPServerCore.IOTPRequest import IOPTServiceType
            if self.service_type is IOPTServiceType.IOTP:
                # check for token
                token = self.formatted_req["token"]
                token_h = s4hash(self.conf_username_h + self.conf_password_h)
                if token is not None:
                    # TODO validate token
                    if token_h != token:
                        # token not matched
                        break
                    self.type = TOKEN
                else:
                    # check request type
                    # TODO validate username & password
                    username = self.formatted_req["username"]
                    password = self.formatted_req["password"]
                    try:
                        username_h = s4hash(username)
                        password_h = s4hash(password)
                        if str(self.conf_username_h) != username_h or str(self.conf_password_h) != password_h:
                            # invalid username or password
                            break
                        self.type = SIGN_IN
                    except:
                        # something wrong in username/password
                        break
            status = True

            break
        if status:
            return token_h
        else:
            return None
