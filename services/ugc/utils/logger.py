import json
import logging
import os
from logging.handlers import RotatingFileHandler

LOGS_DIR = './logs'

os.makedirs(LOGS_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_message = {
            'message': record.getMessage(),
            'request_id': record.request_id,
            'host': record.host,
            'method': record.method,
            'query_params': record.query_params,
            'status_code': record.status_code,
            'elapsed_time': record.elapsed_time
        }

        return json.dumps(log_message)


app_name = 'auth'

log_file = os.path.join(LOGS_DIR, "logs.log")
max_bytes = 10 * 1024 * 1024
backup_count = 5

logger = logging.getLogger(app_name)
logger.setLevel(logging.INFO)

formatter = JsonFormatter()

rotating_file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
rotating_file_handler.setFormatter(formatter)
rotating_file_handler.setLevel(logging.INFO)

logger.addHandler(rotating_file_handler)
