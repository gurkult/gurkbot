from loguru import logger
import os

# set up logging

log_dir = 'log'
log_file = log_dir + os.sep + 'gurkbot.log'
os.makedirs(log_dir, exist_ok=True)


def should_rotate(message, file):
    """When should the bot rotate : Once in 1 week or if the size is greater than 5 MB"""
    filepath = os.path.abspath(file.name)
    creation = os.path.getmtime(filepath)
    now = message.record["time"].timestamp()
    max_time = 7 * 24 * 60 * 60  # 1 week in seconds
    if file.tell() + len(message) > 5 * (2 ** 20):  # if greater than size 5 MB
        return True
    if now - creation > max_time:
        return True


logger.add(log_file, rotation=should_rotate)
logger.info('Logging Process Started')
