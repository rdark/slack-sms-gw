import logging
from slack_sms_gw.config import LoggingConfig
from sys import stdout


def logger(name: str, config: LoggingConfig) -> logging.Logger:
    log = logging.getLogger(name)
    if config.stdout:
        h = logging.StreamHandler(stdout)
        h.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        h.setLevel(config.level)
        log.addHandler(h)
    log.setLevel(config.level)
    return log
