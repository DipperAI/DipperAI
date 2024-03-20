import json
import requests
from maas.core import MaaS
from version import __version__


class Modelscope(MaaS):
    def __init__(
        self,
        model_url=None,
        model_id=None,
        model_version="master",
        cloud=None,
        config=None,
        url=None,
        debug=False,
    ):
        """Initialize the Modelscope instance.

        :param model_url: The URL of the model.
        :param model_id: The ID of the model.
        :param model_version: The version of the model, default is "master".
        :param cloud: The cloud provider.
        :param config: The configuration for the model.
        :param url: The URL for the model.
        :param debug: A flag indicating whether to run in debug mode.
        """
        super().__init__(
            model_url, model_id, model_version, cloud, config, url, debug
        )
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "dipperai@%s" % __version__,
        }
        self.token = None

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
