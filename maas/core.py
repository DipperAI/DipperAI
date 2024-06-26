import importlib
import hashlib
import requests
from vendor import Devs
from utils.logger import setup_logger
from utils.cache import OperateCache, cache

model_default_error = "Model service exception."
model_check_error = "Model service check failed."
model_update_error = "Model service update failed."
model_create_error = "Model service create failed."


class MaaS:

    def __init__(self, model_url=None, model_id=None, model_version="master", cloud=None, service_config=None,
                 service_url=None, debug=False):
        """
        init default vars
        :param model_url: model url, like: https://modelscope.cn/models/iic/cv_convnextTiny_ocr-recognition-general_damo/summary
        :param model_id: model name / model id
        :param model_version: model version
        :param cloud: cloud/vendor attr, like: Alibaba(), AWS(), AIGCaaS()
        :param service_config: function/container config
        :param service_url: service url
        :param debug: debug mode
        """
        self.default_resource_name = None
        self.service_url = service_url
        self.model_id = model_id
        self.model_url = model_url
        self.model_version = model_version
        self.maas_name = self.__class__.__name__.lower()
        self.logger = setup_logger(debug=debug)
        self.vendor = cloud or Devs(logger=self.logger)
        self.model_meta = self.get_model_meta()
        self.resource_name = self.get_resource_name()
        self.service_config = self.get_service_config(service_config)
        # 部署模型
        if not self.__deploy():
            raise Exception("Failed to deploy model to cloud.")

    def get_config_func_name(self) -> str:
        """
        get resource name
        :return: str
        """
        return str("%s_%s_default_config" % (self.maas_name, self.vendor.__class__.__name__)).lower()

    def get_service_config(self, user_config: dict) -> dict:
        """
        get service config
        :return: dict
        """
        # 补充配置
        config_func_name = self.get_config_func_name()
        lib_module = importlib.import_module('resources.config')
        return getattr(lib_module, config_func_name)(user_config)

    def get_model_meta(self) -> dict:
        """
        the MaaS module needs to rewrite this method, primarily for handling the model_url.
        It involves parsing the model_url to extract the model_id and model_version.
        :return: dict
        """
        return {}

    def check_config(self, new: dict, old: dict) -> bool:
        """
        compare the current configuration with the user specified configuration
        :param new: user newly specified configuration
        :param old: current configuration, or default configuration
        :return: comparison results, True / False
                    True: indicates consistency
                    False: indicates inconsistency (requires update operation)
        """
        for key, value in new.items():
            if key not in old:
                print(key)
                return False
            if isinstance(value, dict):
                if not isinstance(old[key], dict) or not self.check_config(value, old[key]):
                    print(key)
                    return False
            elif old[key] != value:
                print(key)
                return False
        return True

    def get_resource_name(self) -> str:
        """
        Generate a resource name based on MaaS name, model ID, and model version.
        If `default_resource_name` is provided, it will be returned otherwise
        a hash-based unique identifier is generated as part of the name.

        :return: A string representing the resource name.
        """
        if self.default_resource_name:
            return self.default_resource_name
        hash_code = hashlib.sha256(f'{self.maas_name}-{self.model_id}-{self.model_version}'.encode()).hexdigest()[:10]
        resource_name = f'dipperai-{self.maas_name}-{hash_code}'
        return resource_name.replace("/", "-")

    def __deploy(self) -> bool:
        """
        get service url; the main func of maas
        :return: service url
        """
        # Basic guard clause. If service URL is already set, deployment has been completed.
        if self.service_url:
            return True

        # get cache
        #   1. get cache success:
        #     1.1 config mismatching: update
        #       1.1.1 update success: return
        #       1.1.2 update failed: raise exception
        #       1.1.3 update unknown: raise exception
        #     1.2 config matching: return
        #   2. get cache failed: continue
        with OperateCache(cache) as cache_data:
            cache_model_info = cache_data.get_cache(self.resource_name)
            if cache_model_info and cache_model_info.get("url"):
                if not self.check_config(self.service_config, cache_model_info.get("config", {})):
                    update_result = self.vendor.update(self.resource_name, self.service_config)
                    if update_result and update_result.get("url") and update_result.get("config"):
                        cache_data.set_cache(self.resource_name, update_result)
                        self.service_url = update_result["url"]
                        self.service_config = update_result["config"]
                        return True
                    else:
                        raise BaseException(model_update_error)
                self.logger.info(f"Model {self.resource_name} already deployed.")
                self.service_url = cache_model_info["url"]
                return True

            # create resources
            #    1. create resources success: return
            #    2. create resources failed: raise exception
            #    3. create resources unknown: raise exception
            create_result = self.vendor.create(self.resource_name, self.service_config)
            if create_result and create_result.get("url") and create_result.get("config"):
                cache_data.set_cache(self.resource_name, create_result)
                self.service_url = create_result["url"]
                self.service_config = create_result["config"]
                return True
            else:
                raise BaseException(model_create_error)

    def invoke(self, input: any, headers: dict = None) -> dict:
        """
        invoke MaaS
        :param input: input data
        :return: MaaS output
        """
        self.logger.info(f"Invoke {self.maas_name}: {self.service_url}")
        return requests.post(self.service_url, json=input, headers=headers).json()
