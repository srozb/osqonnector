import logging
import logging.handlers
import config


class Logger(object):
    console_log_format = "%(asctime)-15s osqonnector[%(process)d] %(name)s %(message)s"
    syslog_log_format = "osqonnector[%(process)d]: %(name)s %(message)s"

    def __init__(self, mod_name):
        self.logger = logging.getLogger(mod_name)
        self.logger.setLevel(config.LOG_LEVEL)

        if config.DAEMON:
            self.formatter = logging.Formatter(self.syslog_log_format)
            self.handler = logging.handlers.SysLogHandler(
                address=config.SYSLOG_ADDR)
        else:
            self.formatter = logging.Formatter(self.console_log_format)
            self.handler = logging.StreamHandler()
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def debug(self, buf):
        self.logger.debug(buf)

    def info(self, buf):
        self.logger.info(buf)

    def warn(self, buf):
        self.logger.warn(buf)

    def error(self, buf):
        self.logger.error(buf)

    def critical(self, buf):
        self.logger.critical(buf)
