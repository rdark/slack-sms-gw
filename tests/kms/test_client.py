from tests.helpers.config import minimal_aws_slack_sms_gw_config
from tests.helpers.kms import KmsClientHelper
import uuid
import pytest
from moto import mock_kms
from hashlib import sha256
from base64 import urlsafe_b64encode


@pytest.fixture(scope="function")
def aws_credentials(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")


@pytest.fixture(scope="function")
def kms_client_helper_moto(aws_credentials, minimal_aws_slack_sms_gw_config) -> KmsClientHelper:
    with mock_kms():
        client = KmsClientHelper(
            log_config=minimal_aws_slack_sms_gw_config.logging,
            config=minimal_aws_slack_sms_gw_config.aws)
        client.kms_client.key_id = client.generate_kms_key()
        yield client


@pytest.fixture(scope="function")
def kms_client_helper_fake_encrypt(aws_credentials, minimal_aws_slack_sms_gw_config, monkeypatch) -> KmsClientHelper:
    """Used elsewhere to avoid moto monkeypatching messing with requests"""
    client = KmsClientHelper(
        log_config=minimal_aws_slack_sms_gw_config.logging,
        config=minimal_aws_slack_sms_gw_config.aws)
    client.kms_client.key_id = "test-key"
    monkeypatch.setattr(client.kms_client, "encrypt", client.encrypt_static)
    return client


def test_mock_encrypt(kms_client_helper_moto):
    message = kms_client_helper_moto.kms_client.encrypt("Foo")
    assert message.kms_key_id == kms_client_helper_moto.kms_client.key_id
    uuid.UUID(message.encryption_context["message_id"])
    # TODO - better test
    assert len(message.ciphertext) > 10


def test_fake_encrypt(kms_client_helper_fake_encrypt):
    message = kms_client_helper_fake_encrypt.kms_client.encrypt("Foo")
    assert message.kms_key_id == kms_client_helper_fake_encrypt.kms_client.key_id
    uuid.UUID(message.encryption_context["message_id"])
    assert urlsafe_b64encode(bytes(sha256("Foo".encode("utf-8")).hexdigest(), "utf-8")).decode("utf-8") == \
        message.ciphertext

