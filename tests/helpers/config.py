from slack_sms_gw.config import (
    SlackSmsGwConfig,
    slack_sms_gw_config_env_builder
)
import pytest


@pytest.fixture(scope="function")
def minimal_slack_sms_gw_config(monkeypatch) -> SlackSmsGwConfig:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "foo")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "bar")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://localhost/a/web/hook")
    return slack_sms_gw_config_env_builder()


@pytest.fixture(scope="function")
def minimal_aws_slack_sms_gw_config(monkeypatch) -> SlackSmsGwConfig:
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "foo")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "bar")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://localhost/a/web/hook")
    monkeypatch.setenv("AWS_KMS_KEY_ID", "baz")
    monkeypatch.setenv("AWS_REGION", "ap-southeast-1")
    return slack_sms_gw_config_env_builder()
