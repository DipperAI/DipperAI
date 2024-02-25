from vendor import Alibaba
from utils.logger import setup_logger
from utils.cache import set_cache, get_cache

model_default_error = "Model service exception."
model_check_error = "Model service check failed."
model_update_error = "Model service update failed."
model_create_error = "Model service create failed."


class MaaS:

    def __init__(self, model_url=None, model_id=None, model_version="master", cloud=None, config=None, url=None, debug=False):
        """
        init default vars
        :param model_url: model url, like: https://modelscope.cn/models/iic/cv_convnextTiny_ocr-recognition-general_damo/summary
        :param model_id: model name / model id
        :param model_version: model version
        :param cloud: cloud/vendor attr, like: Alibaba(), AWS(), AIGCaaS()
        :param config: function/container config
        :param url: service url
        :param debug: debug mode
        """
        self.default_resource_name = None
        self.url = url
        self.config = config
        self.model_id = model_id
        self.model_url = model_url
        self.model_version = model_version
        self.logger = setup_logger(debug=debug)
        self.maas_name = self.__class__.__name__
        self.vendor = cloud or Alibaba(config, self.logger)

    def init(self):
        pass

    def check_config(self, current_config=None):
        """
        compare the current configuration with the user specified configuration
        :param current_config: current configuration
        :return: comparison results, True / False
                    True: indicates consistency
                    False: indicates inconsistency (requires update operation)
        """
        if current_config is None: current_config = {}


    def get_url(self):
        """
        get service url; the main func of maas
        :return: service url
        """
        if self.url: return self.url
        self.init()
        self.default_resource_name = f'dipperai-{self.maas_name}-{self.model_id}-{self.model_version}'
        # special attention should be paid to whether the name will exceed the maximum value
        # for example, a length of 64 is the upper limit
        self.default_resource_name = self.default_resource_name.replace("/", "-")
        # get cache
        #   1. get cache success:
        #     1.1 config mismatching: update
        #       1.1.1 update success: return
        #       1.1.2 update failed: raise exception
        #       1.1.3 update unknown: raise exception
        #     1.2 config matching: return
        #   2. get cache failed: continue
        cache_model_info = get_cache(self.default_resource_name)
        if cache_model_info.get("url"):
            if not self.check_config(cache_model_info.get("config", {})):
                update_result = self.vendor.update(self.default_resource_name, self.config)
                if not update_result.get("url"): raise BaseException(update_result.get("error", model_update_error))
                set_cache(self.default_resource_name, update_result)
            return cache_model_info["url"]
        # check resource
        #   1. check resource success: return
        #     1.1 config mismatching: update
        #       1.1.1 update success:
        #       1.1.2 update failed:
        #       1.1.3 update unknown:
        #     1.2 config matching: return
        #   2. check resource failed: raise exception
        #   3. check resource unknown: continue
        check_result = self.vendor.check(self.default_resource_name, self.config)
        if check_result.get("url"):
            if not self.check_config(check_result.get("config")):
                update_result = self.vendor.update(self.default_resource_name, self.config)
                if not update_result.get("url"): raise BaseException(update_result.get("error", model_update_error))
                set_cache(self.default_resource_name, update_result)
            else:
                set_cache(self.default_resource_name, check_result)
            return check_result["url"]
        if check_result.get("error"): raise BaseException(check_result.get("error", model_check_error))
        # create resource
        #    1. create resource success: return
        #    2. create resource failed: raise exception
        #    3. create resource unknown: raise exception
        create_result = self.vendor.create(self.default_resource_name, self.config)
        if create_result.get("url"):
            set_cache(self.default_resource_name, create_result)
            return create_result["url"]
        if create_result.get("error"): raise BaseException(create_result.get("error", model_create_error))
        raise BaseException(create_result.get("error", model_default_error))
