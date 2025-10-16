from typing import Optional, Any

import logging
import os
import environ
from logging.handlers import TimedRotatingFileHandler
from dataclasses import dataclass
from energydeskapi.sdk.common_utils import load_class_from_string
import importlib

logger = logging.getLogger(__name__)

import socket

@dataclass(frozen=True)
class LogstashConfig:
    host: str
    port : int
    customer: str= "cust1"
    environment: str = "dev1"
    appname: str = "SDK"

def get_environment_value(parameter: str, default: Any) -> Any:
    env = environ.Env()
    outvalue = default
    if parameter in os.environ:
        outvalue = env(parameter)
    return outvalue

def get_logfile_format(servicetag):
    format="%(asctime)s srv_" + servicetag + " %(name)-12s %(levelname)-8s %(message)s"
    return format

def get_logstash_format():
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    return format

def get_consolelog_format():
    format="%(asctime)s %(levelname)-8s %(message)s"
    return format

def get_loglevel_from_str(strlevel: str) -> int:
    if strlevel=="DEBUG":
        return logging.DEBUG
    if strlevel=="INFO":
        return logging.INFO
    if strlevel=="WARNING":
        return logging.WARNING
    if strlevel=="ERROR":
        return logging.ERROR
    return logging.INFO

def get_loglevel_to_str(level: int) -> str:
    if level==logging.DEBUG:
        return "DEBUG"
    if level==logging.INFO:
        return "INFO"
    if level==logging.WARNING:
        return "WARNING"
    if level==logging.ERROR:
        return "ERROR"
    return "INFO"

def setup_service_logging(servicetag: str, file_level: int=logging.INFO, console_level: int=logging.INFO, enable_logstash_conf:LogstashConfig=None):
    console_level=get_loglevel_from_str(get_environment_value("OVERRIDE_CONSOLE_LOGLEVEL", get_loglevel_to_str(console_level)))
    file_level=get_loglevel_from_str(get_environment_value("OVERRIDE_FILE_LOGLEVEL", get_loglevel_to_str(file_level)))

    def create_console_handler() -> logging.StreamHandler:
        console = logging.StreamHandler()
        formatter_console = logging.Formatter(get_consolelog_format())
        console.setFormatter(formatter_console)
        console.setLevel(console_level)
        return console

    def create_tcp_handler(host, port):
        env = environ.Env()
        loglev = "INFO" if "LOGSTASH_LOGLEVEL" not in env else env.str("LOGSTASH_LOGLEVEL")
        handler_class = load_class_from_string("logstash_async.handler.AsynchronousLogstashHandler") #pip install python-logstash before enabling this
        handler = handler_class(
            host,
            port,
            database_path='/tmp/django-logstash.db',
            version=1,
            tags=[enable_logstash_conf.customer, enable_logstash_conf.environment, enable_logstash_conf.appname],
            ssl_enable=True,
            ssl_verify=False
        )
        handler.setLevel(get_loglevel_from_str(loglev))
        # Lazy import SingleLineLogstashFormatter
        module = importlib.import_module('energydeskapi.sdk.logstash_singleline_formatter')
        SingleLineLogstashFormatter = getattr(module, 'SingleLineLogstashFormatter')
        formatter = SingleLineLogstashFormatter(
            message_type='python-logstash',
            fqdn=False,
            extra_prefix='extra',
            extra={
                'logstash_async_version': '4.0.2',
                'customer': enable_logstash_conf.customer,
                'environment': enable_logstash_conf.environment,
                'appname': enable_logstash_conf.appname
            }
        )
        handler.setFormatter(formatter)
        return handler

    def create_file_handler()-> TimedRotatingFileHandler:
        try:
            os.makedirs('./logs', exist_ok=True)
        except:
            pass
        filelogger = TimedRotatingFileHandler('./logs/' + servicetag + '.log', 'midnight', 1)
        filelogger.setLevel(file_level)
        formatter_file = logging.Formatter(get_logfile_format(servicetag))
        filelogger.setFormatter(formatter_file)
        return filelogger

    def valid_handlers(handlers_with_possible_none: list[Optional[logging.Handler]]) -> list[logging.Handler]:
        return [h for h in handlers_with_possible_none if h is not None]

    file_handler = create_file_handler()
    console_handler = create_console_handler()
    tcp_handler = create_tcp_handler(enable_logstash_conf.host, enable_logstash_conf.port) if enable_logstash_conf is not None else None
    print(f"file_handler: {file_handler}")
    print(f"console_handler: {console_handler}")
    print(f"tcp_handler: {tcp_handler}")
    logging.basicConfig(force=True, level=min(console_level, file_level), handlers=valid_handlers([console_handler, file_handler, tcp_handler]))

# Just to make setup simpler with some standardized env names
def create_logstash_from_environment():
    env=environ.Env()
    enabled = False if "LOGSTASH_ENABLED" not in env else env.bool("LOGSTASH_ENABLED")
    if enabled:
        host = None if "LOGSTASH_HOST" not in env else env.str("LOGSTASH_HOST")
        port = None if "LOGSTASH_PORT" not in env else env.int("LOGSTASH_PORT")
        if host is not None and port is not None:
            cust_name = "" if "LOGSTASH_CLIENT_CUSTOMER" not in env else env.str("LOGSTASH_CLIENT_CUSTOMER")
            app_name = "" if "LOGSTASH_CLIENT_APP" not in env else env.str("LOGSTASH_CLIENT_APP")
            env_name = "" if "LOGSTASH_CLIENT_ENVIRONMENT" not in env else env.str("LOGSTASH_CLIENT_ENVIRONMENT")
            return LogstashConfig(host, port, cust_name, env_name, app_name)
        else:
            return None
    else:
        return None