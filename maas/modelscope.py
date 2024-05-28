import importlib
import json
import os

import requests
from maas.core import MaaS
from version import __version__


class Modelscope(MaaS):
    def __init__(self, model_id: str, model_version: str = "master", service_config: dict = None,
                 cloud: any = None, service_url: str = None):
        """Initialize the Modelscope instance.
        :param model_id: The ID of the model.
        :param model_version: The version of the model, default is "master".
        :param service_config: The configuration for the model.
        :param cloud: The cloud provider.
        :param service_url: The URL of the model.
        """
        self.region = os.environ.get("MS_REGION", "cn-hangzhou")
        self.access_token = os.environ.get("DASHSCOPE_API_KEY", None)
        self.model_version = model_version
        super().__init__(model_id=model_id, model_version=model_version, cloud=cloud,
                         service_config=service_config, service_url=service_url)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "dipperai@%s" % __version__,
        }

    def get_service_config(self, user_config: dict) -> dict:
        """
        get service config
        :return: dict
        """
        # 补充配置
        config_func_name = self.get_config_func_name()
        lib_module = importlib.import_module('resources.config')
        return getattr(lib_module, config_func_name)(user_config, model_id=self.model_id, region=self.region,
                                                     model_version=self.model_version, access_token=self.access_token)

    def login(self):
        """
        login to modelscope, get cookie and add it to self.headers;
        source code: https://modelscope.cn/docs/api_docs/API文档%2Fbuild%2Fjson%2F_modules%2Fmodelscope%2Fhub%2Fapi%2F%23HubApi.login
        :return:
        """
        login_url = "https://modelscope.cn/api/v1/login"
        payload = json.dumps({"AccessToken": self.access_token})
        response_attr = requests.request("POST", login_url, headers=self.headers, data=payload)
        self.headers["Cookie"] = response_attr.cookies

    def get_task(self):
        """
        get modelscope model task type, automatically generated in file configuration.json;
        source code: https://modelscope.cn/docs/api_docs/API文档%2Fbuild%2Fjson%2F_modules%2Fmodelscope%2Fhub%2Ffile_download%2F%23model_file_download
        :return: Task type (https://modelscope.cn/docs/模型的推理Pipeline#当前支持的task列表)
        """
        file_url = 'https://modelscope.cn/api/v1/models/%s/repo?Revision=%s&FilePath=configuration.json' % (
            self.model_id, self.model_version)
        if self.token: self.login()
        response_json = json.loads(requests.request("POST", file_url, headers=self.headers).content.decode("utf-8"))
        return response_json["task"]
