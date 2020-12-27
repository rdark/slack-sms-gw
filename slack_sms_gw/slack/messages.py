from slack_sms_gw.models import SmsMessage, EncryptedMessage
from dataclasses import fields
from datetime import datetime
from enum import Enum
from typing import Dict, List


def intro_message(message: SmsMessage) -> List[object]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"New SMS message received from *{message.from_number}* via _{message.provider.name}_"
            }
        }, {
            "type": "divider"
        }
    ]


def plain_message(message: SmsMessage) -> List[object]:
    field_list = []
    # Slack "fields" are limited to 10 rows so naively try and trim information
    # then stop appending if we hit 10
    count = 0
    for f in fields(message):
        if count >= 10:
            break
        value = getattr(message, f.name)
        if value is None:
            continue
        if f.name == "sms_status":
            continue
        elif f.name == "provider":
            continue
        if isinstance(value, datetime):
            value = value.isoformat()
        elif isinstance(value, Enum):
            value = value.name
        elif not isinstance(value, str):
            value = str(value)
        field_list += [{
            "type": "plain_text",
            "text": f.name
        }, {
            "type": "plain_text",
            "text": value
        }]
        count += 1
    return [{
        "type": "section",
        "fields": field_list
    }]


def secure_message(encrypted_message: EncryptedMessage) -> List[object]:
    """
    Construct secure (kms encrypted) type message.
    """
    default_field_list = []
    for f in fields(encrypted_message):
        value = getattr(encrypted_message, f.name)
        if value is None:
            continue
        if f.name == "encryption_context":
            continue
        default_field_list += [{
            "type": "plain_text",
            "text": f.name
        }, {
            "type": "plain_text",
            "text": value
        }]
    blocks = [{
        "type": "section",
        "fields": default_field_list
    }, {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*Encryption Context*"
        }
    }, {
        "type": "divider"
    }]
    enc_context_field_list = [{
        "type": "mrkdwn",
        "text": "*Key*"
    }, {
        "type": "mrkdwn",
        "text": "*Value*"
    }]
    for k, v in encrypted_message.encryption_context.items():
        enc_context_field_list += [{
            "type": "plain_text",
            "text": k
        }, {
            "type": "plain_text",
            "text": v
        }]
    blocks.append({
        "type": "section",
        "fields": enc_context_field_list
    })
    return blocks


def decryption_instruction_message(encrypted_message: EncryptedMessage) -> Dict[str, str]:
    decrypt_cmd = f'echo "{encrypted_message.ciphertext}" | base64 --decode | aws kms decrypt fileb:///dev/stdin ' \
                  f'--output text --query Plaintext --encryption-context'
    context_str = ",".join([f"{k}={v}" for k, v in encrypted_message.encryption_context.items()])
    return {
        "text": f'_Decrypt with:_ `{decrypt_cmd} {context_str} | jq .`'
    }
