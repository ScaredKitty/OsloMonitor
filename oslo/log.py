import logging
import logging.config
import socket

HOSTNAME = socket.gethostname()


def format_log_info(hostname):
    return "[%(asctime)s] {0}/%(levelname)s/%(name)s: %(message)s".format(hostname)


# Global flag that we set to True if any unhandled exception occurs in a greenlet
# Used by main.py to set the process return code to non-zero
unhandled_greenlet_exception = False


def setup_logging(logLevel):
    logLevel = logLevel.upper()

    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": format_log_info(HOSTNAME),
            },
            "plain": {
                "format": "%(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "console_plain": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
            },
        },
        "loggers": {
            "oslo": {
                "handlers": ["console"],
                "level": logLevel,
                "propagate": False,
            }
        },
        "root": {
            "handlers": ["console"],
            "level": logLevel,
        }
    }

    logging.config.dictConfig(LOGGING_CONFIG)


def greenlet_exception_logger(logger, level=logging.CRITICAL):
    """
    Return a function that can be used as argument to Greenlet.link_exception() that will log the
    unhandled exception to the given logger.
    """

    def exception_handler(greenlet):
        logger.log(level, "Unhandled exception in greenlet: %s", greenlet, exc_info=greenlet.exc_info)
        global unhandled_greenlet_exception
        unhandled_greenlet_exception = True

    return exception_handler
