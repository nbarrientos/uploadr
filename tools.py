import uuid
import random

from tornado.options import options

from lib.CaptchasDotNet import CaptchasDotNet

def validate_reference(reference):
    try:
        uuid.UUID(reference)
    except ValueError:
        return False
    return True

def generate_token(prefix):
    base = range(97,123)
    base.extend(range(48,58))
    random.shuffle(base)
    base = base[len(base)/2:]
    return prefix + "".join(chr(c) for c in base)

def generate_download_token():
    return generate_token("d")

def generate_remove_token():
    return generate_token("r")

def format_filesize(size):
    units = ("B", "KiB", "MiB", "GiB", "TiB")
    units_index = 0;
    while size >= 1024:
        units_index += 1
        size = size / 1024.0

    # Strip superflous positions
    if units_index > 0:
        size = "%.2f" % size
    else:
        size = "%u" % size

    return (size, units[units_index])

def obtain_captcha_service():
    return CaptchasDotNet(client='demo', 
        secret='secret')

def devel_env():
    ret = False
    if options.environment == "development":
        ret = True
    return ret
