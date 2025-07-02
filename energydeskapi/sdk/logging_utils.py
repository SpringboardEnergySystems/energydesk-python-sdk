
import logging
import os
from logging.handlers import TimedRotatingFileHandler


import os

import environ


def get_environment_value(parameter, default):
    env = environ.Env()
    outvalue = default
    if parameter in os.environ:
        outvalue = env(parameter)
    return outvalue

def get_logfile_format(servicetag):
    format="%(asctime)s srv_" + servicetag + " %(name)-12s %(levelname)-8s %(message)s"
    return format

def get_consolelog_format():
    format="%(asctime)s %(levelname)-8s %(message)s"
    return format

def get_loglevel_from_str(strlevel):
    if strlevel=="DEBUG":
        return logging.DEBUG
    if strlevel=="INFO":
        return logging.INFO
    if strlevel=="WARNING":
        return logging.WARNING
    if strlevel=="ERROR":
        return logging.ERROR
    return logging.INFO

def get_loglevel_to_str(level):
    if level==logging.DEBUG:
        return "DEBUG"
    if level==logging.INFO:
        return "INFO"
    if level==logging.WARNING:
        return "WARNING"
    if level==logging.ERROR:
        return "ERROR"
    return "INFO"

def setup_service_logging(servicetag: str, file_level=logging.WARNING, console_level=logging.INFO):
    console_level=get_loglevel_from_str(get_environment_value("OVERRIDE_CONSOLE_LOGLEVEL", get_loglevel_to_str(console_level)))
    file_level=get_loglevel_from_str(get_environment_value("OVERRIDE_FILE_LOGLEVEL", get_loglevel_to_str(file_level)))

    def create_console_handler() -> logging.StreamHandler:
        console = logging.StreamHandler()
        formatter_console = logging.Formatter(get_consolelog_format())
        console.setFormatter(formatter_console)
        console.setLevel(console_level)
        return console

    def create_file_handler() -> TimedRotatingFileHandler:
        try:
            os.mkdir("./logs")
        except:
            pass
        filelogger = TimedRotatingFileHandler('./logs/' + servicetag + '.log', 'midnight', 1)
        filelogger.setLevel(file_level)
        formatter_file = logging.Formatter(get_logfile_format(servicetag))
        filelogger.setFormatter(formatter_file)
        return filelogger

    file_handler = create_file_handler()
    console_handler = create_console_handler()
    print(f"file_handler: {file_handler}")
    print(f"console_handler: {console_handler}")
    logging.basicConfig(force=True, handlers=[console_handler, file_handler])





