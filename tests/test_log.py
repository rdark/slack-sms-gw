from slack_sms_gw.config import (
    env_config_builder,
    LoggingConfig,
)
from slack_sms_gw.log import logger
import logging
import pytest


def test_logger(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("LOG_STDOUT", "TRUE")
    cfg = env_config_builder(LoggingConfig)
    log = logger(__name__, cfg)
    assert log.level == logging.DEBUG
    log.info("foo")

