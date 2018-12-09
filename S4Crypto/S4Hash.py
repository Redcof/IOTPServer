import base64
import hashlib

_author_ = "int_soumen"
_date_ = "16-09-2018"

def s4hash(string):
    string = "5acf45" + string + "ed13c5"
    encod = base64.b64encode(string)
    part1 = encod[0:8]
    part2 = "5acf45" + string
    m = hashlib.md5()
    m.update(part1 + part2)
    return str(m.hexdigest())



