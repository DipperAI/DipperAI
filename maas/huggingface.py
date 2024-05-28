import os
import importlib
import requests
from maas.core import MaaS
from vendor import Alibaba


class HuggingFace(MaaS):
    def __init__(self, model_id: str, model_version: str = "master", service_config: dict = None,
                 cloud: any = None, service_url: str = None):
        self.region = os.environ.get("HF_REGION", "cn-beijing")
        self.access_token = os.environ.get("HF_ACCESS_TOKEN", None)
        self.hf_endpoint = os.environ.get("HF_ENDPOINT") or "https://huggingface.co"
        super().__init__(model_id=model_id, model_version=model_version, cloud=cloud,
                         service_config=service_config, service_url=service_url)

    def get_model_meta(self):
        """
        从huggingface.co获取模型的元数据。
        
        该方法构造一个请求URL，然后发送GET请求以获取指定模型的元数据。
        
        参数:
        - self: 对象自身的引用，包含模型的ID和访问huggingface.co的端点。
        
        返回值:
        - 返回一个JSON对象，包含从huggingface.co获取到的模型元数据。
        """
        # 构造请求元数据的URL
        meta_url = f"{self.hf_endpoint}/api/models/{self.model_id}"
        # 发送GET请求获取元数据
        r = requests.get(meta_url)
        # 如果请求状态码不是200，抛出异常
        if r.status_code != 200:
            raise Exception("Failed to get model meta data from huggingface.co")
        # 返回解析后的JSON响应
        return r.json()

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

    def __get_library(self) -> str:
        """
        获取模型库地址
        """
        return self.model_meta["library_name"]

    def __get_task(self) -> str:
        """
        获取任务标识

        本方法用于从模型元数据中提取出pipeline标签，作为当前任务的标识。

        参数:
        self - 对象本身的引用。

        返回值:
        str - model_meta字典中"pipeline_tag"键对应的值，表示当前任务的标识。
        """
        return self.model_meta["pipeline_tag"]
