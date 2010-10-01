import uuid

def validate_reference(reference):
    try:
        uuid.UUID(reference)
    except ValueError:
        return False
    return True
