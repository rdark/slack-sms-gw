from slack_sms_gw.types import EnvLookup
from distutils.util import strtobool
from dataclasses import dataclass
from typing import Optional, TypeVar, Type
from os import environ
import logging


class WithEnvLookup:
    @staticmethod
    def env_lookup() -> EnvLookup:
        pass


T = TypeVar("T", bound=WithEnvLookup)


def env_config_builder(cfg_type: Type[T]) -> T:
    found_kwargs = {}
    for k in cfg_type.env_lookup().keys():
        found_kwargs[k] = cfg_type.env_lookup()[k]
    return cfg_type(**found_kwargs)  # type: ignore[call-arg]


@dataclass(frozen=True)
class LoggingConfig(WithEnvLookup):
    stdout: bool
    level: int

    @staticmethod
    def env_lookup() -> EnvLookup:
        return {
            "stdout": bool(strtobool(environ.get("LOG_STDOUT", "false").lower())),
            "level": getattr(logging, environ.get("LOG_LEVEL", "INFO")),
        }


@dataclass(frozen=True)
class TwilioConfig(WithEnvLookup):
    account_sid: str
    auth_token: str

    @staticmethod
    def env_lookup() -> EnvLookup:
        return {
            "account_sid": environ["TWILIO_ACCOUNT_SID"],
            "auth_token": environ["TWILIO_AUTH_TOKEN"],
        }


@dataclass(frozen=True)
class SlackConfig(WithEnvLookup):
    webhook_url: str
    request_timeout: int
    send_decrypt_instructions: bool

    @staticmethod
    def env_lookup() -> EnvLookup:
        return {
            "webhook_url": environ["SLACK_WEBHOOK_URL"],
            "request_timeout": int(environ.get("SLACK_REQUEST_TIMEOUT", "10")),
            "send_decrypt_instructions": bool(
                strtobool(environ.get("SLACK_SEND_DECRYPT_INSTRUCTIONS", "true").lower())),
        }


@dataclass(frozen=True)
class AwsConfig(WithEnvLookup):
    kms_key_id: Optional[str]
    region: Optional[str]

    @staticmethod
    def env_lookup() -> EnvLookup:
        return {
            "kms_key_id": environ.get("AWS_KMS_KEY_ID"),
            "region": environ.get("AWS_REGION"),
        }


@dataclass(frozen=True)
class SlackSmsGwConfig:
    twilio: TwilioConfig
    slack: SlackConfig
    aws: AwsConfig
    logging: LoggingConfig


def slack_sms_gw_config_env_builder() -> SlackSmsGwConfig:
    return SlackSmsGwConfig(
        twilio=env_config_builder(TwilioConfig),
        slack=env_config_builder(SlackConfig),
        aws=env_config_builder(AwsConfig),
        logging=env_config_builder(LoggingConfig),
    )
