from tests.twilio.test_client import (
    twilio_client_helper,
    twilio_message_params
)
from tests.slack.test_client import slack_client_helper_ok
from tests.kms.test_client import (
    aws_credentials,
    kms_client_helper_fake_encrypt
)
from tests.helpers.config import (
    minimal_slack_sms_gw_config,
    minimal_aws_slack_sms_gw_config
)
from slack_sms_gw.router import router
from datetime import datetime
import json
import pytest
# TODO - DRY/simplify


def test_router_receive_plain_twilio_message(twilio_client_helper,
                                             slack_client_helper_ok,
                                             minimal_slack_sms_gw_config,
                                             twilio_message_params,
                                             monkeypatch):
    path = "/twilio/plain"
    base_url, headers = twilio_client_helper.twilio_request(
        path=path,
        params=twilio_message_params,
    )
    headers["x-forwarded-proto"] = base_url.split("://")[0]
    body = twilio_client_helper.encode_body(twilio_message_params)
    now = datetime.utcnow()
    event = {
        "headers": headers,
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": "POST"
            },
            "domainName": base_url.split("://")[1],
            "timeEpoch": now.timestamp(),
        },
        "body": body,
    }
    receiver, receiver_args = router(event)
    monkeypatch.setattr(receiver, "twilio", twilio_client_helper.twilio_client)
    monkeypatch.setattr(receiver, "slack", slack_client_helper_ok.slack_client)
    response = receiver(minimal_slack_sms_gw_config) \
        .receive(*receiver_args)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"


def test_router_receive_secure_twilio_message(twilio_client_helper,
                                              slack_client_helper_ok,
                                              minimal_aws_slack_sms_gw_config,
                                              kms_client_helper_fake_encrypt,
                                              twilio_message_params,
                                              monkeypatch):
    path = "/twilio/secure"
    base_url, headers = twilio_client_helper.twilio_request(
        path=path,
        params=twilio_message_params,
    )
    headers["x-forwarded-proto"] = base_url.split("://")[0]
    body = twilio_client_helper.encode_body(twilio_message_params)
    now = datetime.utcnow()
    event = {
        "headers": headers,
        "rawPath": path,
        "requestContext": {
            "http": {
                "method": "POST"
            },
            "domainName": base_url.split("://")[1],
            "timeEpoch": now.timestamp(),
        },
        "body": body,
    }
    receiver, receiver_args = router(event)
    monkeypatch.setattr(receiver, "twilio", twilio_client_helper.twilio_client)
    monkeypatch.setattr(receiver, "slack", slack_client_helper_ok.slack_client)
    monkeypatch.setattr(receiver, "kms", kms_client_helper_fake_encrypt.kms_client)
    response = receiver(minimal_aws_slack_sms_gw_config) \
        .receive(*receiver_args)
    assert response["statusCode"] == 200
    assert response["headers"]["Content-Type"] == "application/json"


def test_router_not_found(twilio_client_helper, minimal_slack_sms_gw_config):
    now = datetime.utcnow()
    event = {
        "rawPath": "/does-not-exist",
        "headers": {
            "x-forwarded-proto": "https"
        },
        "requestContext": {
            "http": {
                "method": "POST"
            },
            "domainName": "foo.bar",
            "timeEpoch": now.timestamp(),
        },
    }
    receiver, receiver_args = router(event)
    response = receiver(minimal_slack_sms_gw_config) \
        .receive(*receiver_args)
    assert response["statusCode"] == 404
    assert json.loads(response["body"])["message"] == "not found"
