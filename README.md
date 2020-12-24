# Slack SMS Gateway Lambda

A mostly-complete AWS lambda function for receiving SMS messages via an SMS provider and posting them to a slack channel.

* Works with API Gateway
* Supports Twilio as SMS provider
* Supports signature validation for received Twilio webhooks
* Optionally supports encrypted slack messages via AWS KMS


## Routes

### `/twilio/plain`

Messages received via this endpoint will be posted to slack in plain-text:

![Plain SMS Slack Message](https://raw.githubusercontent.com/rdark/slack-sms-gw/master/doc/img/plain_sms.png)

### `/twilio/secure`

Messages received via this endpoint will be posted to slack in encrypted format, optionally with CLI decryption instructions:

![Secure SMS Slack Message](https://raw.githubusercontent.com/rdark/slack-sms-gw/master/doc/img/secure_sms.png)


