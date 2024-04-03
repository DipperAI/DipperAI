import os
import json
from utils.logger import setup_logger

cache_file_dir = os.path.join(os.getcwd(), ".cache")
cache_file = os.path.join(cache_file_dir, "dipperai.json")
logger = setup_logger(
    debug=True if os.environ.get("dipperai_debug_model", None) else False
)

class Cache:
    def __init__(self):
        self.cache_file = self.init_cache()
        self.cache_data = self.load_cache()
        self.change = False

    def save_cache(self):
        """
        persistence cache file.
        """
        if self.change:
            with open(self.cache_file, "w") as f:
                f.write(json.dumps(self.cache_data))
            logger.info("update cache file")

    def init_cache(self):
        """Init cache file, if exist return, else create cache file; cache file path: {run-path}/.cache/dipperai.json.

        :return:
        """
        if not os.path.exists(cache_file):
            os.makedirs(cache_file_dir, exist_ok=True)
            with open(cache_file, "w") as f:
                f.write("{}")
        return cache_file

    def load_cache(self) -> dict:
        """
        Load the cache file.
        """
        try:
            with open(cache_file) as f:
                cache_data = json.loads(f.read())
            return cache_data
        except Exception as e:
            logger.error(e)
            # If the file format is abnormal, the cache will be cleared
            os.remove(cache_file)
            self.init_cache()
            return {}

    def get_cache(self, key:str=None) -> dict:
        """Get the value by the key from the cache file.

        :param key:
        :return:
        """
        return self.cache_data.get(key, {})


    def set_cache(self, key:str, value:str) -> bool:
        """Set the key and the value to cache file.

        :param key:
        :param value:
        :return:
        """
        if self.cache_data.get(key, {}) != value:
            self.cache_data[key] = value
            self.change = True
        return True

class OperateCache:

    def __init__(self, cache:Cache):
        self.cache = cache
    
    def __enter__(self):
        return self.cache

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_to_file()
    
    def _save_to_file(self):
        cache.save_cache()

# 全局cache对象, 相当于单例模式，只有在第一次调用时初始化
# 避免每次调用都初始化，提高性能
cache = Cache()