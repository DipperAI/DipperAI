import os
import dashscope
from typing import Any, Dict, List, Union
from maas.core import MaaS
from utils.logger import setup_logger

logger = setup_logger()


class TongYi(MaaS):
    def __init__(self, model_id: str):
        self.api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self.model_id = model_id

    def invoke(self, input: dict, headers: dict = None) -> dict:
        """
        调用模型，生成文本
        参数:
            input (dict): 对齐 TongYi API 的输入参数，如 prompt、result_format 等，但无需再次指定模型 ID 和 API_KEY
        返回:
            dict: 生成的文本或回应的其它形式
        """
        response = dashscope.Generation.call(model=self.model_id, api_key=self.api_key, **input)
        return response
