from slack_sms_gw.types import UriParams, Headers
from slack_sms_gw.models import SmsMessage, SmsProvider
from slack_sms_gw.twilio.exceptions import SignatureValidationError
from slack_sms_gw.config import TwilioConfig, LoggingConfig
from slack_sms_gw.log import logger
from base64 import urlsafe_b64decode
from datetime import datetime
from urllib.parse import parse_qsl
from twilio.rest import Client
from twilio.request_validator import RequestValidator


class TwilioClient:
    def __init__(self, log_config: LoggingConfig, config: TwilioConfig) -> None:
        self.log = logger(self.__class__.__name__, config=log_config)
        self.config = config
        self.client = Client(self.config.account_sid, self.config.auth_token)
        self.request_validator = RequestValidator(self.config.auth_token)
        self._twilio_sig_header = "x-twilio-signature"
        self._ip_header = "x-forwarded-for"

    def compute_signature(self, uri: str, params: UriParams):
        return self.request_validator.compute_signature(uri, params)

    def validate_request(self, uri: str, params: UriParams, signature: str):
        return self.request_validator.validate(uri, params, signature)

    def receive_message(self, uri: str, body: str, timestamp: float, headers: Headers) -> SmsMessage:
        self.log.info(f"received message of length {len(body)} at uri {uri} " +
                      f"with signature {headers[self._twilio_sig_header]}")
        params: UriParams = dict(
            parse_qsl(urlsafe_b64decode(body).decode("utf-8"), keep_blank_values=True)
        )
        if not self.validate_request(uri=uri, params=params, signature=headers[self._twilio_sig_header]):
            msg = f"message signature invalid: {headers[self._twilio_sig_header]}"
            self.log.error(msg)
            raise SignatureValidationError(msg)

        return SmsMessage(
            sms_status=params["SmsStatus"],
            provider=SmsProvider.TWILIO,
            body=params["Body"],
            to_number=params["To"],
            from_number=params["From"],
            received_at=datetime.utcfromtimestamp(timestamp),
            from_ip=headers.get(self._ip_header),
            to_country=params.get("ToCountry"),
            from_country=params.get("FromCountry"),
            from_state=params.get("FromState"),
            from_city=params.get("FromCity"),
            from_zip=params.get("FromZip"),
        )
