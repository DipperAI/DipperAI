import os
import time
import json
import hmac
import base64
import random
import hashlib
import requests


class Alibaba:

    def __init__(self, ACCESS_KEY_ID=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", None),
                 ACCESS_KEY_SECRET=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", None),
                 SECURITY_TOKEN=os.environ.get("ALIBABA_CLOUD_SECURITY_TOKEN", None),
                 ACCOUNT_ID=os.environ.get("FC_ACCOUNT_ID", None),
                 config=None, logger=None):
        self.config = config
        self.logger = logger
        self.ALIBABA_CLOUD_ACCESS_KEY_ID = ACCESS_KEY_ID
        self.ALIBABA_CLOUD_SECURITY_TOKEN = SECURITY_TOKEN
        self.ALIBABA_CLOUD_ACCESS_KEY_SECRET = ACCESS_KEY_SECRET
        self.endpoint = '1583208943291465.cn-hangzhou.fc.aliyuncs.com'

    def sign_request(self, method, headers, resource):
        """
        alibaba cloud api request sign method;
        docs: https://help.aliyun.com/zh/sdk/product-overview/roa-mechanism?spm=a2c4g.2618586.0.i9
        :param method: request method
        :param headers: request headers
        :param resource: request uri
        :return: signed string, like: "acs keyid:sign"
        """
        string_to_sign = (f"{method}\n{headers.get('accept', '')}\n{headers.get('content-md5', '')}\n"
                          f"{headers.get('content-type', '')}\n{headers.get('date', '')}\n"
                          f"x-acs-signature-method:HMAC-SHA1\n"
                          f"x-acs-signature-nonce:{headers.get('x-acs-signature-nonce', '')}\n"
                          f"x-acs-signature-version:1.0\nx-acs-version:{headers.get('x-acs-version', '')}\n{resource}")
        key_secret_encode = self.ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode('utf-8')
        string_to_sign_encode = string_to_sign.encode('utf-8')
        signature = hmac.new(key_secret_encode, string_to_sign_encode, hashlib.sha1).digest()
        signature = base64.b64encode(signature)
        return f"acs {self.ALIBABA_CLOUD_ACCESS_KEY_ID}:{signature.decode('utf-8')}"

    def get_headers(self):
        """
        get default request headers, include "x-acs-signature" and "x-acs-version";
        :return: request headers
        """
        return {
            "accept": "application/json",
            'date': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime()),
            'host': self.endpoint,
            "x-acs-signature-nonce": str(random.randint(1, 10000)),
            "x-acs-signature-method": "HMAC-SHA1",
            "x-acs-signature-version": "1.0",
            "x-acs-version": "2023-03-30",
            "content-type": "application/json",
            "content-md5": ""
        }

    def get_function(self, function_name):
        """
        get the function detail;
        docs: https://help.aliyun.com/document_detail/2618610.html?spm=a2c4g.2618615.0.0.4b4613f35Qq27z
        :param function_name: function name, default regex: dipperai-{model_platform}-{model_id}-{model_version}
        :return: the request response
        """
        try:
            resource = f"/2023-03-30/functions/{function_name}"
            headers = self.get_headers()
            headers['authorization'] = self.sign_request('GET', headers, resource)
            url = f"https://{self.endpoint}{resource}"
            response_data = requests.get(url, headers=headers).content.decode("utf-8")
            return json.loads(response_data)
        except Exception as e:
            self.logger.error(e)
            return False

    def get_trigger(self, function_name, trigger_name="serverlessai_default_trigger"):
        """
        get the function trigger detail;
        docs: https://help.aliyun.com/document_detail/2618615.html?spm=a2c4g.2618641.0.0.79653c17XYM3S8
        :param function_name: function name, default regex: dipperai-{model_platform}-{model_id}-{model_version}
        :param trigger_name: trigger name, default: dipperai_default_trigger
        :return: the request response
        """
        try:
            resource = f"/2023-03-30/functions/{function_name}/triggers/{trigger_name}"
            headers = self.get_headers()
            headers['authorization'] = self.sign_request('GET', headers, resource)
            url = f"https://{self.endpoint}{resource}"
            response_data = requests.get(url, headers=headers).content.decode("utf-8")
            return json.loads(response_data)
        except Exception as e:
            self.logger.error(e)
            return False

    def create_function(self, function_name):
        """
        create alibaba cloud fc function, default is custom container function;
        docs: https://help.aliyun.com/document_detail/2618641.html?spm=a2c4g.2618639.0.0.393b7c57jVkKrX
        :param function_name: function name, default regex: dipperai-{model_platform}-{model_id}-{model_version}
        :return: created response
        """
        try:
            resource = f"/2023-03-30/functions"
            headers = self.get_headers()
            headers['authorization'] = self.sign_request('POST', headers, resource)
            url = f"https://{self.endpoint}{resource}"
            default_config = {
                "cpu": 0.05,
                "customContainerConfig": {},
                "description": "Serverless AI Project, {model_id}-{model_version}",
                "environmentVariables": {},
                "functionName": function_name,
                "gpuConfig": {

                },
                "role": "",
                "runtime": "custom-container",
                "timeout": 300,

            }
            merged_config = {**default_config, **(self.config or {})}
            response_data = requests.post(url, headers=headers, json=merged_config).content.decode("utf-8")
            return json.loads(response_data)
        except Exception as e:
            self.logger.error(e)
            return False

    def create_trigger(self, function_name, trigger_name="dipperai_default_trigger"):
        """
        create alibaba cloud fc function trigger;
        docs: https://help.aliyun.com/document_detail/2618639.html?spm=a2c4g.2508973.0.0.3d7c7c57JwPHEM
        more: the trigger config detail: https://github.com/devsapp/fc/blob/main/src/lib/interface/fc/trigger.ts
        :param function_name: function name, default regex: serverlessas-{model_id}-{model_version}
        :param trigger_name: trigger name, default: dipperai_default_trigger
        :return: created response
        """
        try:
            resource = f"/2023-03-30/functions/{function_name}/triggers"
            headers = self.get_headers()
            headers['authorization'] = self.sign_request('POST', headers, resource)
            url = f"https://{self.endpoint}{resource}"
            response_data = requests.post(url, headers=headers, json={
                "description": "Serverless AI Project Default HTTP Trigger",
                "qualifier": "LATEST",
                "triggerConfig": {
                    "authType": "anonymous",
                    "methods": ["GET", "POST"]
                },
                "triggerName": trigger_name,
                "triggerType": "http"
            }).content.decode("utf-8")
            return json.loads(response_data)
        except Exception as e:
            self.logger.error(e)
            return False

    def check(self, name, config):
        """
        check function is exist
        :param name: function name
        :param config: function config
        :return: check result
        """
        pass

    def update(self, name, config):
        """
        update the function to the specify config
        :param name: function name
        :param config: function config
        :return: update result
        """
        pass

    def create(self, name, config):
        """
        create the function with the specify config
        :param name: function name
        :param config: function config
        :return: create result
        """
        pass
