from slack_sms_gw.types import EncryptionContext
from dataclasses import (
    dataclass,
    is_dataclass,
    asdict
)
from typing import Optional
from enum import Enum
from json import JSONEncoder
from datetime import datetime


class SmsProvider(Enum):
    TWILIO = 1


@dataclass(frozen=True)
class SmsMessage(object):
    sms_status: str
    provider: SmsProvider
    body: str
    to_number: str
    from_number: str
    received_at: datetime
    from_ip: Optional[str] = None
    to_country: Optional[str] = None
    from_country: Optional[str] = None
    from_city: Optional[str] = None
    from_state: Optional[str] = None
    from_zip: Optional[str] = None


@dataclass(frozen=True)
class EncryptedMessage(object):
    encryption_context: EncryptionContext
    kms_key_id: str
    ciphertext: str


class DefaultModelEncoder(JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.name
        return super().default(obj)

