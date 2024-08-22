import logging  # 引入logging模块


# proxylog.basicConfig函数对日志的输出格式及方式做相关配置
class Logger(object):
    def __init__(self):
        # 日志等级（从小到大）：
        # debug()-->info()-->warning()-->error()-->critical()
        # Step 1: Loggers, 并设置全局level
        self.logger = logging.getLogger('proxy_log')
        self.logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        fh = logging.FileHandler('../proxylog.txt')


        fh.setLevel(logging.DEBUG)
        my_formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]%(message)s')
        ch.setFormatter(my_formatter)
        fh.setFormatter(my_formatter)
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def debug(self, msg):
        self.logger.debug(f'  [*]  {msg}')

    def info(self, msg):
        self.logger.info(f'  [+]  {msg}')

    def warning(self, msg: str):
        self.logger.warning(f'  [!]  {msg}')

    def error(self, msg):
        self.logger.error(f'  [x]  {msg}')

    def critical(self, msg):
        self.logger.critical(f'  [~]  {msg}')
