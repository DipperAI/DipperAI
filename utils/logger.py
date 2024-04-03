import logging
from colorama import init, Fore, Style

init(autoreset=True)

# define a new log level
SUCCESS = 25
logging.addLevelName(SUCCESS, "SUCCESS")
DEFAULT_FORMAT = "[%(asctime)s] [%(levelname)s]] "


def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS):
        self._log(SUCCESS, message, args, **kws)


logging.Logger.success = success


class CustomFormatter(logging.Formatter):
    """define custom formatter.

    # grey: debug
    # green: success
    # yellow: warning
    # red: error.
    """

    grey = Style.DIM + Fore.WHITE
    green = Fore.GREEN
    yellow = Fore.YELLOW
    red = Fore.RED
    reset = Style.RESET_ALL

    def format(self, record):
        """Rewrite format style.

        :param record: record attr
        :return: message with new style.
        """
        log_fmt = DEFAULT_FORMAT
        if record.levelno == SUCCESS:
            log_fmt += f"{self.green}%(message)s{self.reset}"
        elif record.levelno == logging.INFO:
            log_fmt += "%(message)s"
        elif record.levelno == logging.WARNING:
            log_fmt += f"{self.yellow}%(message)s{self.reset}"
        elif record.levelno == logging.ERROR:
            log_fmt += f"{self.red}%(message)s{self.reset}"
        elif record.levelno == logging.CRITICAL:
            log_fmt += f"{self.red}%(message)s{self.reset}"
        else:
            log_fmt += "%(message)s"
        formatter = logging.Formatter(log_fmt, "%Y-%m-%d %H:%M:%S")
        record.message = formatter.format(record)
        return record.message


def setup_logger(debug=False):
    """Set logger attr.

    :param debug: if True, will show debug message, else will not show debug message
    :return: logger attr.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    # 检查是否已经添加了处理程序
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(CustomFormatter())
        logger.addHandler(console_handler)
    else:
        # 可选：更新现有处理程序的日志级别
        for handler in logger.handlers:
            handler.setLevel(logging.DEBUG if debug else logging.INFO)

    return logger