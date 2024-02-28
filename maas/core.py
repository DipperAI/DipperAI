import importlib
from vendor import Alibaba
from utils.logger import setup_logger
from utils.cache import set_cache, get_cache

model_default_error = "Model service exception."
model_check_error = "Model service check failed."
model_update_error = "Model service update failed."
model_create_error = "Model service create failed."


class MaaS:
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
        """Init default vars.

        :param model_url: model url, like: https://modelscope.cn/models/iic/cv_convnextTiny_ocr-recognition-general_damo/summary
        :param model_id: model name / model id
        :param model_version: model version
        :param cloud: cloud/vendor attr, like: Alibaba(), AWS(), AIGCaaS()
        :param config: function/container config
        :param url: service url
        :param debug: debug mode.
        """
        self.default_resource_name = None
        self.url = url
        self.config = config
        self.model_id = model_id
        self.model_url = model_url
        self.model_version = model_version
        self.logger = setup_logger(debug=debug)
        self.maas_name = self.__class__.__name__
        self.vendor = cloud or Alibaba(config=config, logger=self.logger)

    def model_info(self, model_url, model_id, model_version, config):
        """The MaaS module needs to rewrite this method, primarily for handling the model_url. It involves parsing the model_url to extract the model_id and model_version.

        :param model_url: model url
        :param model_id: model id / name
        :param model_version: model version
        :param config: config
        :return: model_id, model_version(default: "master"), config.
        """
        return model_id, model_version, config

    def check_config(self, sub_dict, super_dict):
        """Compare the current configuration with the user specified configuration.

        :param sub_dict: user newly specified configuration
        :param super_dict: current configuration, or default configuration
        :return: comparison results, True / False
                    True: indicates consistency
                    False: indicates inconsistency (requires update operation).
        """
        for key, value in sub_dict.items():
            if key not in super_dict:
                return False
            if isinstance(value, dict):
                if not isinstance(super_dict[key], dict):
                    return False
                if not self.check_config(value, super_dict[key]):
                    return False
            else:
                if super_dict[key] != value:
                    return False
        return True

    def get_url(self):
        """Get service url; the main func of maas.

        :return: service url.
        """
        if self.url:
            return self.url
        self.model_id, self.model_version, self.config = self.model_info(
            self.model_url, self.model_id, self.model_version, self.config
        )
        self.default_resource_name = (
            f"dipperai-{self.maas_name}-{self.model_id}-{self.model_version}"
        )
        # special attention should be paid to whether the name will exceed the maximum value
        # for example, a length of 64 is the upper limit
        self.default_resource_name = self.default_resource_name.replace(
            "/", "-"
        )
        config_func_name = str(
            f"{self.maas_name}_{self.vendor.__class__.__name__}_default_config"
        ).lower()
        lib_module = importlib.import_module("resources.config")
        config = getattr(lib_module, config_func_name)(
            self.default_resource_name, self.config
        )
        # get cache
        #   1. get cache success:
        #     1.1 config mismatching: update
        #       1.1.1 update success: return
        #       1.1.2 update failed: raise exception
        #       1.1.3 update unknown: raise exception
        #     1.2 config matching: return
        #   2. get cache failed: continue
        cache_model_info = get_cache(self.default_resource_name)
        if cache_model_info and cache_model_info.get("url"):
            if not self.check_config(
                self.config, cache_model_info.get("config", {})
            ):
                update_result = self.vendor.update(
                    self.default_resource_name, config
                )
                if not update_result.get("url"):
                    raise BaseException(
                        update_result.get("error", model_update_error)
                    )
                set_cache(self.default_resource_name, update_result)
            return cache_model_info["url"]
        # check resources
        #   1. check resources success: return
        #     1.1 config mismatching: update
        #       1.1.1 update success:
        #       1.1.2 update failed:
        #       1.1.3 update unknown:
        #     1.2 config matching: return
        #   2. check resources failed: raise exception
        #   3. check resources unknown: continue
        check_result = self.vendor.check(self.default_resource_name, config)
        if check_result.get("url"):
            if not self.check_config(self.config, check_result.get("config")):
                update_result = self.vendor.update(
                    self.default_resource_name, config
                )
                if not update_result.get("url"):
                    raise BaseException(
                        update_result.get("error", model_update_error)
                    )
                set_cache(self.default_resource_name, update_result)
            else:
                set_cache(self.default_resource_name, check_result)
            return check_result["url"]
        if check_result.get("error"):
            raise BaseException(check_result.get("error", model_check_error))
        # create resources
        #    1. create resources success: return
        #    2. create resources failed: raise exception
        #    3. create resources unknown: raise exception
        create_result = self.vendor.create(self.default_resource_name, config)
        if create_result.get("url"):
            set_cache(self.default_resource_name, create_result)
            return create_result["url"]
        if create_result.get("error"):
            raise BaseException(create_result.get("error", model_create_error))
        raise BaseException(create_result.get("error", model_default_error))
