import uuid
from datetime import datetime


def generate_unique_login():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    unique_login = f"{uuid.uuid4().hex}_{timestamp}"
    return unique_login
