import uuid
import random

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
    return generate_token("dt")

def generate_remove_token():
    return generate_token("") # Fixme

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
