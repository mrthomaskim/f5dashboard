import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from time import sleep
import logfactory
import json

logger = logfactory.create(__name__)

class Token(object):
    def __init__(self):
        logger.debug("Token..")
    def build_body(self, userid, password):
        self.body = {
            "username" : userid,
            "password" : password,
            "loginProviderName" : "tmos"
        }
        return self.body
    def get_token(self, url, body):
        r = requests.post(url, json=body, verify=False)
        #return (r.json())['token']['token']
        return (r.json())


class Http(object):
    def __init__(self, base_url, userid, password):
        logger.debug("Http...")
        login_path = '/shared/authn/login'
        url = base_url + login_path
        creds = Token()
        body  = creds.build_body(userid, password)
        rtn_code = creds.get_token(url, body)
        self.token_exp_time = rtn_code['token']['expirationMicros']
        token = rtn_code['token']['token']
        self.headers = {
                    "Content-Type": "application/json",
                    "X-F5-Auth-Token": token
        }
    def get(self, url):
        return requests.get(url, headers=self.headers, verify=False).json()
    def paged_get(self, url, params={}):
        response = []
        offset = 0
        params["limit"] = 90
        while True:
            params["offset"] = offset
            while True:
                reply = requests.get(url, headers=self.headers, params=params)
                if reply.status_code == 403:
                    print("Rate limited: pause and retry")
                    sleep(5)
                    continue
                break
            json = reply.json()
            response = response + json
            if json["total"] == len(response):
                return response
            offset += params["limit"]
