from slack_sms_gw.models import (
    SmsMessage,
    EncryptedMessage,
    DefaultModelEncoder,
    SmsProvider
)
import json
from datetime import datetime
import pytest


def test_sms_message_encode():
    msg = SmsMessage(
        sms_status="received",
        provider=SmsProvider.TWILIO,
        body="Foo",
        to_number="12346",
        from_number="1235",
        received_at=datetime.utcnow()
    )
    json.dumps(msg, cls=DefaultModelEncoder, indent=2)


def test_encrypted_message_encode():
    msg = EncryptedMessage(
        encryption_context={"foo": "bar"},
        kms_key_id="foo",
        ciphertext="foobars",
    )
    json.dumps(msg, cls=DefaultModelEncoder, indent=2)
