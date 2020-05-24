import datetime
import hashlib, string, random


def get_current_time():
    current = str(datetime.datetime.now())
    arr = current.split(" ")
    ymd = arr[0]
    hms = arr[1]
    ymd1 = ymd.replace("-", "")
    hms1 = hms.replace(":", "")
    result_msg = ymd1 + "".join(hms1.split("."))
    return result_msg


def get_md5(str_md5):
    md5 = hashlib.md5()
    md5.update(str_md5.encode("utf-8"))
    token = md5.hexdigest()
    return token.lower()


def return_data(msg,data=None):
    if data is not None:
        return {
            "code": 1,
            "msg": msg,
            "data": data
        }
    else:
        return {
            "code": 0,
            "msg":msg
        }


def get_code():
    '''
    随机生成32位乱码，由字母，数字和特殊符号
    '''
    return "".join(random.sample(string.ascii_letters + string.digits, 32))
