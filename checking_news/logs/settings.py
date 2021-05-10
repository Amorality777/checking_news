import sys

from loguru import logger

msg_fmt = '<g>{time:DD.MM.YY HH:mm:ss}</g> | <level>{level}</level> | <y>{name}:{function}:{line}</y> | <c>{message}</c>'

logger.remove()
logger.add(sink=sys.stdout, colorize=True, level='DEBUG', format=msg_fmt)
logger.add(sink=f'logs/debug.log', level='DEBUG', format=msg_fmt, rotation='00:00')
logger.add(sink=f'logs/error.log', level='ERROR', format=msg_fmt, rotation='00:00')


def setup_logger():
    return logger
