from tests.helpers.slack import SlackClientHelper
from tests.helpers.kms import KmsClientHelper
from tests.helpers.config import minimal_slack_sms_gw_config
from slack_sms_gw.slack.messages import (
    intro_message,
    plain_message,
    secure_message
)
from slack_sms_gw.models import (
    SmsMessage,
    SmsProvider,
    DefaultModelEncoder
)
from datetime import datetime
import json
import pytest


@pytest.fixture(scope="function")
def slack_client_helper_ok(minimal_slack_sms_gw_config, monkeypatch):
    client = SlackClientHelper(
        log_config=minimal_slack_sms_gw_config.logging,
        config=minimal_slack_sms_gw_config.slack,
    )
    monkeypatch.setattr(client.slack_client, "send", SlackClientHelper.mock_send_ok)
    return client


@pytest.fixture(scope="function")
def twilio_sms_message():
    return SmsMessage(
        sms_status="received",
        provider=SmsProvider.TWILIO,
        body="The message",
        to_number="+12346892345",
        from_number="+12312481245",
        received_at=datetime.utcnow()
    )


@pytest.fixture(scope="function")
def encrypted_message(twilio_sms_message):
    return KmsClientHelper.encrypt_static(
        json.dumps(twilio_sms_message, cls=DefaultModelEncoder))


def test_plain_message(twilio_sms_message):
    msg = plain_message(twilio_sms_message)
    assert msg[0]["fields"][0]["text"] == "body"
    assert msg[0]["fields"][1]["text"] == twilio_sms_message.body


def test_secure_message(encrypted_message):
    msg = secure_message(encrypted_message)
    assert msg[0]["fields"][0]["text"] == "kms_key_id"
    assert msg[0]["fields"][1]["text"] == encrypted_message.kms_key_id


def test_send_plain_message_ok(slack_client_helper_ok, twilio_sms_message):
    msg = {
        "blocks": intro_message(twilio_sms_message) + plain_message(twilio_sms_message)
    }
    resp = slack_client_helper_ok.slack_client.post_webhook(data=json.dumps(msg))
    assert resp.status_code == 200
    assert resp.text == "ok"


def test_send_secure_message(slack_client_helper_ok, twilio_sms_message, encrypted_message):
    msg = {
        "blocks": intro_message(twilio_sms_message) + secure_message(encrypted_message)
    }
    resp = slack_client_helper_ok.slack_client.post_webhook(data=json.dumps(msg))
    assert resp.status_code == 200
    assert resp.text == "ok"

