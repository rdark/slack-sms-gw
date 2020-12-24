from slack_sms_gw.config import (
    LoggingConfig,
    SlackConfig
)
from slack_sms_gw.log import logger
from requests import (
    Request,
    Response,
    Session,
    PreparedRequest,
    HTTPError,
    RequestException
)


class SlackClient:
    def __init__(self, log_config: LoggingConfig, config: SlackConfig):
        self.log = logger(self.__class__.__name__, config=log_config)
        self.config = config
        self.webhook_url = self.config.webhook_url
        self.request_timeout = self.config.request_timeout
        self._session = Session()
        self._headers = {
            "POST": {
                "Content-Type": "application/json",
            }
        }

    def post_webhook(self, data: str) -> Response:
        """Convenience method to just send a message to the webhook URL"""
        return self.send(request=self.request("POST", data=data))

    def headers(self, method):
        return self._headers[method]

    def request(self, method: str, data: str) -> PreparedRequest:
        req = Request(method=method,
                      url=self.webhook_url,
                      data=data,
                      headers=self.headers(method))
        return self._session.prepare_request(req)

    def send(self, request: PreparedRequest) -> Response:
        try:
            res = self._session.send(
                request=request,
                timeout=self.request_timeout)
            res.raise_for_status()
        except HTTPError as e:
            msg = f"HTTPError sending {request.method} to {request.url}: " + \
                f"{e}: {res.status_code}"
            if hasattr(res, "text"):
                msg += f" text: {res.text}"
            self.log.error(msg)
            raise e
        except (ConnectionError, TimeoutError) as e:
            self.log.error(f"error connecting to {request.url}: {e}")
            raise e
        except RequestException as e:
            self.log.error(f"unknown error occurred connecting to {request.url}: {e}")
            raise e
        return res
