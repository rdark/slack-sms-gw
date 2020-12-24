from slack_sms_gw.config import (
    LoggingConfig,
    AwsConfig,
)
from slack_sms_gw.models import EncryptedMessage
from slack_sms_gw.kms.client import KmsClient
from base64 import urlsafe_b64encode
from hashlib import sha256


class KmsClientHelper:
    def __init__(self, log_config: LoggingConfig, config: AwsConfig):
        self.log_config = log_config
        self.config = config
        self.kms_client = KmsClient(
            log_config=self.log_config,
            config=self.config,
        )

    def generate_kms_key(self) -> str:
        key = self.kms_client.client.create_key(Description="test-key")
        return key["KeyMetadata"]["KeyId"]

    @staticmethod
    def encrypt_static(plaintext: str) -> EncryptedMessage:
        """Fake encrypt method"""
        context = KmsClient.generate_encryption_context()
        return EncryptedMessage(
            encryption_context=context,
            kms_key_id="test-key",
            ciphertext=urlsafe_b64encode(
                bytes(sha256(plaintext.encode("utf-8")).hexdigest(), "utf-8")).decode("utf-8")
        )
