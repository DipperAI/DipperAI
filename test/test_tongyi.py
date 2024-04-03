import os
import dashscope
import unittest
import random
from maas.tongyi import TongYi

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit"
                        ]
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]


class TestTongYi(unittest.TestCase):
    def setUp(self):
        self.model_id = dashscope.Generation.Models.qwen_plus  # 使用 qwen_plus 模型
        self.tongyi = TongYi(model_id=self.model_id)

    def test_invoke_with_prompt(self):
        # 测试prompt参数
        inputs = {"prompt": "What is the meaning of life?"}
        response = self.tongyi.invoke(inputs)

        # 检查响应是否正确
        self.assertEqual(response.status_code, 200)

    def test_invoke_with_messages(self):
        messages = [{'role': 'user', 'content': 'What is the weather like in Beijing?'}]
        inputs = {"messages": messages, "tools": tools, "seed": random.randint(1, 10000)}

        response = self.tongyi.invoke(inputs)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
