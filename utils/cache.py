import os
import json
from utils.logger import setup_logger

cache_file_dir = os.path.join(os.getcwd(), ".cache")
cache_file = os.path.join(cache_file_dir, "dipperai.json")
logger = setup_logger(
    debug=True if os.environ.get("dipperai_debug_model", None) else False
)


def init_cache():
    """Init cache file, if exist return, else create cache file; cache file path: {run-path}/.cache/dipperai.json.

    :return:
    """
    if not os.path.exists(cache_file):
        os.makedirs(cache_file_dir, exist_ok=True)
        with open(cache_file, "w") as f:
            f.write("{}")
    return cache_file


def get_cache(key=None):
    """Get the value by the key from the cache file.

    :param key:
    :return:
    """
    try:
        init_cache()
        with open(cache_file) as f:
            temp_data = json.loads(f.read())
        return temp_data.get(key, None) if key else temp_data
    except Exception as e:
        logger.error(e)
        # If the file format is abnormal, the cache will be cleared
        os.remove(cache_file)
        init_cache()
        return {}


def set_cache(key, value):
    """Set the key and the value to cache file.

    :param key:
    :param value:
    :return:
    """
    temp_data = get_cache(key=None)
    temp_data[key] = value
    with open(cache_file, "w") as f:
        f.write(json.dumps(temp_data))
    return True
