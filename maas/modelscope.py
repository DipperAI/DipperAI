import re
import json
import requests
from maas.core import MaaS
from version import __version__


class Modelscope(MaaS):

    def __init__(self, model_url=None, model_id=None, model_version="master", cloud=None, config=None, url=None, debug=False):
        super().__init__(model_url, model_id, model_version, cloud, config, url, debug)
        self.headers = {'Content-Type': 'application/json', "User-Agent": "dipperai@%s" % __version__}
        self.token = None

    def model_info(self, model_url, model_id, model_version, config):
        """
        rewrite core file model_info func; get model information
        :param model_url: model url
        :param model_id: model id / name
        :param model_version: model version
        :param config: config
        :return: model_id, model_version(default: "master"), config
        """
        if model_url and not model_id:
            model_id = re.findall("modelscope\.cn/models/(.*?)/summary", model_url)
            if len(model_id) == 0: raise BaseException("Incorrect provision of model_URL or model_id parameters.")
            model_id = model_id[0]
            model_version = "master"


        return model_id, model_version, config

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
        file_url = 'https://modelscope.cn/api/v1/models/%s/repo?Revision=%s&FilePath=configuration.json' % (
            self.model_id, self.model_version)
        if self.token: self.login()
        response_json = json.loads(requests.request("POST", file_url, headers=self.headers).content.decode("utf-8"))
        return response_json["task"]

    def invoke(self, input_args, batch_size=None):
        """
        invoke func / container / api
        :param input_args: input param
        :param batch_size: batch size param
        :return: response json / string
        """
        self.url = self.get_url()
        json_data = {"input": input_args, "batch_size": batch_size}
        headers = {}
        result = requests.post(self.url, json=json_data, headers=headers).content.decode("utf-8")
        try:
            return json.loads(result)
        except Exception as e:
            self.logger.error(e)
            return result
