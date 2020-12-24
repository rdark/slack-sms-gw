from slack_sms_gw.config import slack_sms_gw_config_env_builder
from slack_sms_gw.router import router

config = slack_sms_gw_config_env_builder()


def lambda_handler(event, _):
    receiver, receiver_args = router(event)
    return receiver(config).receive(*receiver_args)
