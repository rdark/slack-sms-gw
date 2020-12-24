from slack_sms_gw.types import EncryptionContext
from slack_sms_gw.models import EncryptedMessage
from slack_sms_gw.config import (
    LoggingConfig,
    AwsConfig
)
from slack_sms_gw.log import logger
from typing import Optional
from base64 import urlsafe_b64encode
import uuid
import boto3


class KmsClient:
    def __init__(self, log_config: LoggingConfig, config: AwsConfig) -> None:
        self.log = logger(self.__class__.__name__, config=log_config)
        self.config = config
        self._key_id = self.config.kms_key_id
        self.client = boto3.client("kms", region_name=self.config.region)

    @property
    def key_id(self) -> Optional[str]:
        return self._key_id

    @key_id.setter
    def key_id(self, value: str):
        self._key_id = value

    @staticmethod
    def generate_encryption_context() -> EncryptionContext:
        return {"message_id": str(uuid.uuid4())}

    def encrypt(self, plaintext: str) -> EncryptedMessage:
        context = self.generate_encryption_context()
        self.log.info(f"encrypting plaintext of length {len(plaintext)}")
        response = self.client.encrypt(
            KeyId=self.key_id,  # type: ignore[arg-type]
            Plaintext=bytes(plaintext, encoding="utf-8"),
            EncryptionContext=context,
        )
        return EncryptedMessage(
            encryption_context=context,
            kms_key_id=self.key_id,  # type: ignore[arg-type]
            ciphertext=urlsafe_b64encode(response["CiphertextBlob"]).decode("utf-8"),
        )
