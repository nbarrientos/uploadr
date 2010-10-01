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
