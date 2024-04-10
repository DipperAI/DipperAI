# test_huggingface.py
import os
import sys
sys.path.append(os.getcwd())
import unittest
from unittest.mock import patch
from maas.huggingface import HuggingFace

class TestHuggingFace(unittest.TestCase):

    def setUp(self):
        self.hf = HuggingFace(
            model_id="distilbert/distilbert-base-uncased-finetuned-sst-2-english",
            # service_config={
            #     "parameters": {
            #         "gpuMemorySize": "15360",
            #         "memorySize": "30720"
            #     }
            # }
        )
        # self.hf = HuggingFace("cardiffnlp/twitter-roberta-base-sentiment-latest")


    def test_invoke_success(self):
        # 模拟返回值

        # 调用invoke方法
        inputs = {'input': 'haha'}
        response = self.hf.invoke(inputs)
        
        print(response)
        # 验证返回的结果是否正确
        # self.assertEqual(response["data"][0]["label"], 'POSITIVE')

# 运行测试
if __name__ == '__main__':
    unittest.main()