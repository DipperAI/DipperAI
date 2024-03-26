import os
import sys
import requests
from maas.core import MaaS
from vendor import Alibaba
from utils.logger import setup_logger

logger = setup_logger()


class HuggingFace(MaaS):
    def __init__(self, model_id: str, model_version: str = None, config: dict = None, 
                  fc_config: dict = None):
        self.model_id = model_id
        self.model_version = model_version or "main"
        self.config = config
        self.fc_url = None
        self.access_token = os.environ.get("HF_ACCESS_TOKEN", None)
        self.hf_endpoint = os.environ.get("HF_ENDPOINT") or "https://huggingface.co"
        self.model_meta = self.__get_meta()
        self.fc_config = fc_config or self.__get_fc_default_config()
        self.alibaba = Alibaba(config=self.fc_config, logger=logger)
        if not self.__deploy_fc():
            raise Exception("Failed to deploy model to alibaba cloud function compute")

    def __get_meta(self):
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

    def __get_fc_name(self) -> str:
        """
        获取函数名称
        """
        return f"huggingface-{self.model_id}-{self.model_version}".replace("/", "-")

    def __get_fc_default_config(self) -> dict:
        """
        获取默认函数配置
        """
        image = "registry.cn-beijing.aliyuncs.com/aliyun-fc/huggingface:transformers-v1" if self.__get_library() == "transformers" else "registry.cn-beijing.aliyuncs.com/aliyun-fc/huggingface:diffusers-v1"
        return {
            "functionName": self.__get_fc_name(),
            "description": "huggingface model",
            "handler": "not-used",
            "timeout": 1800,
            "memorySize": 32768,
            "cpu":2,
            "diskSize": 10240,
            "gpuConfig":{
                "gpuMemorySize":16384,
                "gpuType":"fc.gpu.tesla.1"
            },
            "instanceConcurrency":1,
            "runtime": "custom-container",
            "internetAccess":True,
            "customContainerConfig":{
                "image": image,
                "port": 8000
            },
            "environmentVariables": {
                "MODEL_ID": self.model_id,
                "HUGGING_FACE_HUB_TOKEN": self.access_token,
                "MODEL_TASK": self.__get_task(),
                "HF_HOME": "/mnt/auto/hf",
                "PYTHONPATH": "/docker:/mnt/auto/python",
                "HF_ENDPOINT": "https://hf-mirror.com"
            }
        }

    def __deploy_fc(self):
        """
        部署模型到阿里云函数计算
        """
        fc_name = self.__get_fc_name()
        try:
            # 判断函数是否存在
            if self.alibaba.get_function(fc_name):
                trigger = self.alibaba.get_trigger(fc_name)
                if not trigger:
                    trigger = self.alibaba.create_trigger(fc_name)
            elif self.alibaba.create_function(fc_name, self.fc_config):
                    trigger = self.alibaba.create_trigger(fc_name)
                    logger.info(f"deploy function {fc_name} to alibaba cloud function compute")
            self.fc_url = trigger["httpTrigger"]["urlInternet"]
            logger.debug(f"function {fc_name} trigger url: {self.fc_url}")
            return True
        except Exception as e:
            logger.error(e)
            return False
    
    def invoke(self, inputs) -> dict:
        """
        调用模型
        """
        return requests.post(self.fc_url, json=inputs).json()
        

        
