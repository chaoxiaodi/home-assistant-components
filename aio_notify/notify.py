import logging
import time
import requests
import json

import hmac
import hashlib
import base64
import random
import urllib.parse

from homeassistant.components.notify import (
    ATTR_MESSAGE,
    ATTR_TITLE,
    ATTR_DATA,
    ATTR_TARGET,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)
DIVIDER = "——————————"

def get_service(hass, config, discovery_info=None):
    return DingTalkRobotNotificationService(
        hass,
        config.get("robot"),
        config.get("isatall"),
    )


class DingTalkRobotNotificationService(BaseNotificationService):
    def __init__(self, hass, robot: list, isatall: bool = False):
        self.base_url = 'https://oapi.dingtalk.com/robot/send?access_token='
        self._robot = robot
        self._isatall = isatall

    def dingtalk_sign(self, secret):
        '''
        dingtalk 加签
        '''
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return 'timestamp=%s&sign=%s' % (timestamp, sign)

    
    def send_message(self, message: str = '', **kwargs):
        '''
        暂时只支持markdown类型
        markdown类型 简洁明了 同时又支持url链接和图片能满足大部分需求
        '''
        random_robot = random.choice(self._robot)
        access_token = random_robot['access_token']
        secret = random_robot['secret']
        sign = self.dingtalk_sign(secret)
        base_url = '%s%s&%s' % (self.base_url, access_token, sign)
        title = kwargs.get('title')
        data = kwargs.get('data', {})

        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": title ,
                "text": message
            },
            "at": {
                "atMobiles" : [],
                "isAtAll": self._isatall
            }
        }
        try:
            res = requests.post(base_url, headers=headers, json=data, timeout=3)
            json_text = json.loads(res.text)
            if json_text['errcode'] == 0:
                _LOGGER.info('Send to %s success!' % access_token[-6:])
            else:
                _LOGGER.error('Send to %s failed! with : %s' % (access_token[-6:], res.text))
        except Exception as e:
            _LOGGER.error('Request to dingtalk error: %s' % e)
