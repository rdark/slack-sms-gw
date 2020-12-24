from slack_sms_gw.types import Headers, ApiGatewayHttpResponse
from slack_sms_gw.config import SlackSmsGwConfig
from slack_sms_gw.twilio.client import TwilioClient
from slack_sms_gw.slack.client import SlackClient
from slack_sms_gw.models import DefaultModelEncoder
from slack_sms_gw.slack.messages import (
    intro_message,
    plain_message,
    secure_message,
    decryption_instruction_message
)
from slack_sms_gw.kms.client import KmsClient
from typing import Optional
from slack_sms_gw.log import logger
import json


class BaseReceiver(object):
    def __init__(self, config: SlackSmsGwConfig) -> None:
        self.log = logger(self.__class__.__name__, config=config.logging)
        self.config = config

    def receive(self,
                uri: str,
                body: str,
                timestamp: int,
                headers: Headers) -> ApiGatewayHttpResponse:
        pass


class NotFoundReceiver(BaseReceiver):
    def __init__(self, config: SlackSmsGwConfig):
        super().__init__(config)

    def receive(self,
                uri: str,
                body: str,
                timestamp: int,
                headers: Headers) -> ApiGatewayHttpResponse:
        self.log.error(
            "did not find route for request at " +
            f"uri: {uri} " +
            f"timestamp: {timestamp} " +
            f"headers: {headers}"
        )
        response: ApiGatewayHttpResponse = {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
            },
            "body": '{"message": "not found"}',
        }
        return response


class BaseTwilioSlackReceiver(BaseReceiver):
    def __init__(self, config: SlackSmsGwConfig):
        super().__init__(config)
        self._twilio: Optional[TwilioClient] = None
        self._slack: Optional[SlackClient] = None

    @property
    def twilio(self) -> TwilioClient:
        if not self._twilio:
            self._twilio = TwilioClient(
                config=self.config.twilio,
                log_config=self.config.logging,
            )
        return self._twilio

    @property
    def slack(self) -> SlackClient:
        if not self._slack:
            self._slack = SlackClient(
                config=self.config.slack,
                log_config=self.config.logging,
            )
        return self._slack


class TwilioPlainMessageReceiver(BaseTwilioSlackReceiver):
    def receive(self,
                uri: str,
                body: str,
                timestamp: int,
                headers: Headers) -> ApiGatewayHttpResponse:
        sms_msg = self.twilio.receive_message(
            uri=uri, body=body, timestamp=timestamp / 1000, headers=headers)
        slack_response = self.slack.post_webhook(
            data=json.dumps({
                "blocks": intro_message(sms_msg) + plain_message(sms_msg)
            })
        )
        response: ApiGatewayHttpResponse = {
            "statusCode": slack_response.status_code,
            "headers": {
                "Content-Type": "application/json",
            },
        }
        return response


class TwilioSecureMessageReceiver(BaseTwilioSlackReceiver):
    def __init__(self, config: SlackSmsGwConfig):
        super().__init__(config)
        self._kms: Optional[KmsClient] = None

    def receive(self,
                uri: str,
                body: str,
                timestamp: int,
                headers: Headers) -> ApiGatewayHttpResponse:
        sms_msg = self.twilio.receive_message(
            uri=uri, body=body, timestamp=timestamp / 1000, headers=headers)
        sec_msg = self.kms.encrypt(json.dumps(sms_msg, cls=DefaultModelEncoder))
        slack_response = self.slack.post_webhook(
            data=json.dumps({
                "blocks": intro_message(sms_msg) + secure_message(sec_msg)
            })
        )
        # decryption instructions sent as separate message due to line
        # wrapping in blocks
        if self.config.slack.send_decrypt_instructions:
            self.slack.post_webhook(
                data=json.dumps(decryption_instruction_message(sec_msg))
            )
        response: ApiGatewayHttpResponse = {
            "statusCode": slack_response.status_code,
            "headers": {
                "Content-Type": "application/json",
            },
        }
        return response

    @property
    def kms(self) -> KmsClient:
        if not self._kms:
            self._kms = KmsClient(
                config=self.config.aws,
                log_config=self.config.logging,
            )
        return self._kms
