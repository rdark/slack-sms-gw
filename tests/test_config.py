from tests.helpers.config import minimal_slack_sms_gw_config
from slack_sms_gw.config import (
    LoggingConfig,
    TwilioConfig,
    env_config_builder,
)
import logging
import pytest


def test_logging_config(monkeypatch):
    cfg = env_config_builder(LoggingConfig)
    assert cfg.level == logging.INFO
    monkeypatch.setenv("LOG_LEVEL", "WARN")
    cfg = env_config_builder(LoggingConfig)
    assert cfg.level == logging.WARN


def test_logging_config_env_builder_stdout(monkeypatch):
    cfg = env_config_builder(LoggingConfig)
    assert cfg.stdout is False
    monkeypatch.setenv("LOG_STDOUT", "TRUE")
    cfg = env_config_builder(LoggingConfig)
    assert cfg.stdout is True


def test_env_config_builder(minimal_slack_sms_gw_config):
    cfg = env_config_builder(TwilioConfig)
    assert cfg.account_sid == "foo"
    assert cfg.auth_token == "bar"
