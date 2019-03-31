import base64
import hashlib
import time

_author_ = "int_soumen"
_date_ = "16-09-2018"

# def s4hash(string):
#     string = "5acf45" + string + "ed13c5"
#     encoded_64 = base64.b64encode(string)
#     part1 = encoded_64[0:8]
#     part2 = "5acf45" + string
#     m = hashlib.md5()
#     m.update(part1 + part2)
#     return str(m.hexdigest())


current_milli_time = lambda: int(round(time.time() * 1000))

ENC_KEY = "QKNs:6z.WnpRS^:6"


def s4hash(val):
    salted = encode(val, ENC_KEY)
    return salted


def encode(val, key=None):
    # print "---------- ENCODE --------------"
    # get a random hash
    if key is None:
        key = str(current_milli_time())
    m = hashlib.sha512()
    m.update(key)
    key_hash = str(m.hexdigest())
    # print key_hash + " -- 1"
    # salt + string
    val = key_hash[0:8] + val + key_hash[10:18]
    # print val + " -- 2"
    encoded_64 = base64.b64encode(val)
    # print encoded_64 + " -- 3"
    # make some more pads
    pad1 = encoded_64[0:8]
    # print pad1 + " -- 4"
    pad2 = encoded_64[7:15]
    # print pad2 + " -- 5"
    # prepare final encoded value
    return base64.b64encode(pad1 + encoded_64 + pad2)


def decode(hash):
    # print "---------- DECODE --------------"
    cypher = base64.b64decode(hash)
    # print cypher + " -- 1"
    # remove $pad1
    cypher = cypher[8:]
    # print cypher + " -- 2"
    # remove pad2
    cypher = cypher[0:-8]
    # print cypher + " -- 3"
    # decode
    decoded_64 = base64.b64decode(cypher)
    # print decoded_64 + " -- 4"
    # remove prefix
    salted = decoded_64[8:]
    # print salted + " -- 5"
    plain = salted[:-8]
    return plain
