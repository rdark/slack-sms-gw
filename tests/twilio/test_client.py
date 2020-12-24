from tests.helpers.config import minimal_slack_sms_gw_config
from tests.helpers.twilio import TwilioClientHelper
from slack_sms_gw.config import (
    env_config_builder,
    LoggingConfig,
    TwilioConfig
)
from slack_sms_gw.twilio.exceptions import SignatureValidationError
from datetime import datetime
import pytest


@pytest.fixture(scope="function")
def twilio_client_helper(minimal_slack_sms_gw_config):
    return TwilioClientHelper(
        log_config=env_config_builder(LoggingConfig),
        config=env_config_builder(TwilioConfig),
    )


@pytest.fixture(scope="function")
def twilio_message_params():
    return {
        "SmsStatus": "received",
        "Body": "Hello",
        "To": "+1234568912",
        "From": "+93832489239324832",
    }


def test_valid_twilio_request(twilio_client_helper, twilio_message_params):
    path = "/webhook"
    base_url, headers = twilio_client_helper.twilio_request(
        path=path,
        params=twilio_message_params,
    )
    body = twilio_client_helper.encode_body(twilio_message_params)
    full_url = base_url + path
    now = datetime.utcnow()
    sms = twilio_client_helper.twilio_client.receive_message(
        uri=full_url, body=body, timestamp=now.timestamp(), headers=headers)
    assert sms.sms_status == twilio_message_params["SmsStatus"]
    assert sms.body == twilio_message_params["Body"]
    assert sms.to_number == twilio_message_params["To"]
    assert sms.received_at == now
    assert sms.from_number == twilio_message_params["From"]


def test_invalid_path_twilio_request(twilio_client_helper, twilio_message_params):
    path = "/webhook"
    base_url, headers = twilio_client_helper.twilio_request(
        path=path,
        params=twilio_message_params,
        valid=False,
    )
    body = twilio_client_helper.encode_body(twilio_message_params)
    full_url = f"{base_url}{path}"
    with pytest.raises(SignatureValidationError):
        twilio_client_helper.twilio_client.receive_message(
            uri=full_url, body=body, timestamp=datetime.utcnow().timestamp(), headers=headers)


def test_invalid_body_twilio_request(twilio_client_helper, twilio_message_params):
    params = twilio_message_params
    path = "/webhook"
    base_url, headers = twilio_client_helper.twilio_request(
        path=path,
        params=params,
    )
    params["Body"] = "A Sneaky Replacement Body"
    body = twilio_client_helper.encode_body(twilio_message_params)
    full_url = f"{base_url}{path}"
    with pytest.raises(SignatureValidationError):
        twilio_client_helper.twilio_client.receive_message(
            uri=full_url, body=body, timestamp=datetime.utcnow().timestamp(), headers=headers)

