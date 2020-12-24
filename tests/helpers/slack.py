from slack_sms_gw.config import (
    LoggingConfig,
    SlackConfig
)
from slack_sms_gw.slack.client import SlackClient
from requests import Response, PreparedRequest
from requests.structures import CaseInsensitiveDict


class SlackClientHelper:
    def __init__(self, log_config: LoggingConfig, config: SlackConfig):
        self.log_config = log_config
        self.config = config
        self.slack_client = SlackClient(
            log_config=self.log_config,
            config=self.config,
        )

    @staticmethod
    def mock_send_ok(request: PreparedRequest) -> Response:
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        headers = CaseInsensitiveDict()
        headers["content-type"] = "text/html"
        headers["content-encoding"] = "gzip"
        resp.encoding = headers["content-encoding"]
        resp.headers = headers
        resp._content = b"ok"
        return resp
