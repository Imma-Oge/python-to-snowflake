import os
import logging

os.makedirs('logs', exist_ok=True)

logger = logging.getLogger('pipeline_logger')
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler('logs/pipeline.log')
console = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(lineno)d:%(message)s')

file_handler.setFormatter(formatter)
console.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console)


