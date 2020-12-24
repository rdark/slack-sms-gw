from slack_sms_gw.config import (
    TwilioConfig,
    LoggingConfig,
)
from slack_sms_gw.types import UriParams
from slack_sms_gw.twilio.client import TwilioClient
from typing import Tuple
from urllib.parse import urlencode
from base64 import urlsafe_b64encode
from requests.structures import CaseInsensitiveDict


class TwilioClientHelper:
    def __init__(self, log_config: LoggingConfig, config: TwilioConfig):
        self.config = config
        self.log_config = log_config
        self.twilio_client = TwilioClient(
            log_config=self.log_config,
            config=self.config,
        )

    def twilio_request(self, path: str, params: UriParams, valid: bool = True) -> \
            Tuple[str, CaseInsensitiveDict]:
        base_url = "http://localhost"
        full_url = f"{base_url}{path}" if valid else f"{base_url}{path}/invalid"
        signature = self.twilio_client.compute_signature(full_url, params)
        headers = CaseInsensitiveDict(data={"x-twilio-signature": signature})
        return base_url, headers

    @staticmethod
    def encode_body(params: UriParams) -> bytes:
        return urlsafe_b64encode(bytes(urlencode(params), encoding="utf-8"))
