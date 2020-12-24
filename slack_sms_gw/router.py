from slack_sms_gw.types import ReceiverArgs
from slack_sms_gw.receiver import (
    BaseReceiver,
    TwilioPlainMessageReceiver,
    TwilioSecureMessageReceiver,
    NotFoundReceiver
)
from typing import Dict, Tuple, Any, Type


def routes() -> Dict[str, Dict[str, Type[BaseReceiver]]]:
    return {
        "POST": {
            "/twilio/plain": TwilioPlainMessageReceiver,
            "/twilio/secure": TwilioSecureMessageReceiver,
        }
    }


def router(event: Dict[str, Any]) -> Tuple[Type[BaseReceiver], ReceiverArgs]:
    headers = event['headers']
    path = event['rawPath']
    method = event['requestContext']['http']['method']
    timestamp = event['requestContext']['timeEpoch']
    body = event.get('body', '')
    request_uri = f"{event['headers']['x-forwarded-proto']}://" + \
                  f"{event['requestContext']['domainName']}{path}"
    try:
        return routes()[method][path], (request_uri, body, timestamp, headers)
    except KeyError:
        return NotFoundReceiver, (request_uri, body, timestamp, headers)
