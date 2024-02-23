import json
import requests
from vendor import Alibaba
from version import __version__
from utils.logger import setup_logger
from utils.cache import set_cache, get_cache


class Modelscope:
    def __init__(self, model_url, cloud=None, config=None, url=None, debug=False):
        """

        :param url:
        :param cloud: vendor
        """
        self.model_url = model_url
        self.url = url
        self.logger = setup_logger(debug=debug)
        self.vendor = cloud or Alibaba(config, self.logger)
        self.config = config
        self.service_name = ""
        self.model_id = ""
        self.model_version = ""
        self.headers = {'Content-Type': 'application/json', "User-Agent": "serverlessai@%s" % __version__}


    def login(self):
        """
        login to modelscope, get cookie and add it to self.headers;
        source code: https://modelscope.cn/docs/api_docs/API文档%2Fbuild%2Fjson%2F_modules%2Fmodelscope%2Fhub%2Fapi%2F%23HubApi.login
        :return:
        """
        login_url = "https://modelscope.cn/api/v1/login"
        payload = json.dumps({"AccessToken": self.token})
        response_attr = requests.request("POST", login_url, headers=self.headers, data=payload)
        self.headers["Cookie"] = response_attr.cookies

    def get_task(self):
        """
        get modelscope model task type, automatically generated in file configuration.json;
        source code: https://modelscope.cn/docs/api_docs/API文档%2Fbuild%2Fjson%2F_modules%2Fmodelscope%2Fhub%2Ffile_download%2F%23model_file_download
        :return: Task type (https://modelscope.cn/docs/模型的推理Pipeline#当前支持的task列表)
        """
        file_url = 'https://modelscope.cn/api/v1/models/%s/repo?Revision=%s&FilePath=configuration.json' % (self.model_id, self.model_version)
        if self.token: self.login()
        response_json = json.loads(requests.request("POST", file_url, headers=self.headers).content.decode("utf-8"))
        return response_json["task"]

    def endpoint(self):
        """
        get the model service domain, if could not get the service domain, will call Vendor.deploy();
        function_name = serverlessas-{model_id}-{model-version};
        :return:
        """
        url = self.vendor.get_trigger('serverlessas-%s-%s' % (self.model_id, self.model_version))
        self.url = url if url else self.vendor.deploy()

    def invoke(self, input, batch_size=None, auth=None):
        """

        :param input:
        :param batch_size:
        :return:
        """
        json_data = {"input": input, "batch_size": batch_size}
        headers = {}
        if self.url: return requests.post(self.url, json=json_data, headers=headers).content
