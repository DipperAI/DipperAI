"""The current file is used to configure default resource properties/configurations.

func name regex: {maas_class_name}_{vendor_class_name}_default_config (all letters in lowercase)
  like: modelscope_alibaba_default_config
:param: name: default resource name
:param: config: user specified configuration
:return: specific configuration information that will be used to create resources.
"""


def modelscope_alibaba_default_config(config, **kwargs) -> dict:
    """Get modelscope alibaba function config.

    :param name: function name
    :param config: user config
    :return: config.
    """
    default_config = {
        "cpu": 0.05,
        "customContainerConfig": {},
        "description": "Serverless AI Project, {model_id}-{model_version}",
        "environmentVariables": {},
        "gpuConfig": {
        },
        "role": "",
        "runtime": "custom-container",
        "timeout": 300,
    }
    return

def alibaba_huggingface_default_config(name:str, model_id:str, access_token:str, model_task:str, library:str) -> dict:
        """
        获取默认函数配置
        """
        image = "registry.cn-beijing.aliyuncs.com/aliyun-fc/huggingface:transformers-v1" if library == "transformers" else "registry.cn-beijing.aliyuncs.com/aliyun-fc/huggingface:diffusers-v1"
        return {
            "functionName": name,
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
                "MODEL_ID": model_id,
                "HUGGING_FACE_HUB_TOKEN": access_token,
                "MODEL_TASK": model_task,
                "HF_HOME": "/mnt/auto/hf",
                "PYTHONPATH": "/docker:/mnt/auto/python",
                "HF_ENDPOINT": "https://hf-mirror.com"
            }
        }

def huggingface_alibaba_default_config(config, **kwargs) -> dict:
    """
    返回一个合并了默认配置和用户配置的字典。

    参数:
    - name: 模型名称，当前未使用但可能用于未来扩展。
    - config: 用户提供的配置字典，如果未提供则默认为空字典。
    - **kwargs: 可变的关键字参数，可用于未来的扩展。

    返回值:
    - 一个字典，包含默认配置和用户配置的合并结果。
    """
    return {**alibaba_huggingface_default_config(**kwargs), **(config or {})}
    
