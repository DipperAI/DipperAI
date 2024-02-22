import os
from alibabacloud_fc20230330.client import Client as FC20230330Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

class Alibaba:

    def __init__(self, ACCESS_KEY_ID=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID", None),
                 ACCESS_KEY_SECRET=os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET", None),
                 SECURITY_TOKEN=os.environ.get("ALIBABA_CLOUD_SECURITY_TOKEN", None), config=None):
        self.ALIBABA_CLOUD_ACCESS_KEY_ID = ACCESS_KEY_ID
        self.ALIBABA_CLOUD_ACCESS_KEY_SECRET = ACCESS_KEY_SECRET
        self.ALIBABA_CLOUD_SECURITY_TOKEN = SECURITY_TOKEN
        self.config = config
        config = open_api_models.Config(
            access_key_id=self.ALIBABA_CLOUD_ACCESS_KEY_ID,
            access_key_secret=self.ALIBABA_CLOUD_ACCESS_KEY_SECRET
        )
        config.endpoint = f'<your-account-id>.cn-hangzhou.fc.aliyuncs.com'
        self.client = FC20230330Client(config)


    def deploy(self, function_name):
        try:
            runtime = util_models.RuntimeOptions()
            headers = {}
            try:
                # 复制代码运行请自行打印 API 的返回值
                self.client.create_function_with_options_async({}, headers, runtime)
            except Exception as e:
                # logger.warning(e)
                return False
            # cache
            # xxxxx
            return trigger["endpoint"]
        except Exception as e:
            # logger.warning(e)
            return False

    def endpoint(self, function_name):
        try:
            runtime = util_models.RuntimeOptions()
            trigger = self.client.get_trigger_with_options_async(function_name, 'serverlessai_trigger', {}, runtime)
            trigger_domain = trigger["endpoint"]
            # cache
            # xxxxx
            return trigger["endpoint"]
        except Exception as e:
            # logger.warning(e)
            return False
