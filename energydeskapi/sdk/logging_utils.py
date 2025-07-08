import environ
import logging
import os
import environ
from dataclasses import dataclass
from logging.handlers import TimedRotatingFileHandler
#from logstash_async.handler import AsynchronousLogstashHandler
#from logstash_async.formatter import LogstashFormatter
from energydeskapi.sdk.common_utils import load_class_from_string
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LogstashConfig:
    host: str
    port : int
    appname: str = "pod1"
    environment: str = "dev"



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

def setup_service_logging(servicetag: str, file_level=logging.WARNING, console_level=logging.INFO, enable_logstash_conf:LogstashConfig=None):
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
    handlers=[file_handler, console_handler]

    # Must install logstash with pip before setting this
    if enable_logstash_conf is not None:
        # Configure Logstash handler
        host = enable_logstash_conf.host  # Your Logstash host
        port = enable_logstash_conf.port  # The port Logstash is listening on
        c1=load_class_from_string("logstash_async.handler.AsynchronousLogstashHandler")
        logstash_handler = c1(host, port, database_path='logstash_events.db')
        c2=load_class_from_string("logstash_async.formatter.LogstashFormatter")
        # Optional: Configure a Logstash formatter for structured logging
        logstash_formatter = c2(
            message_type='python-logstash',
            extra_prefix='dev',
            extra=dict(application=enable_logstash_conf.appname, environment=enable_logstash_conf.environment)
        )
        logstash_handler.setFormatter(logstash_formatter)
        handlers.append(logstash_handler)

    logging.basicConfig(force=True, level=min(console_level, file_level),  handlers=handlers)



# Just to make setup simpler with some standardized env names
def create_logstash_from_environment():
    env=environ.Env()
    host = None if "LOGSTASH_HOST" not in env else env.str("LOGSTASH_HOST")
    port = None if "LOGSTASH_PORT" not in env else env.int("LOGSTASH_PORT")
    app = "" if "LOGSTASH_CLIENT_APP" not in env else env.str("LOGSTASH_CLIENT_APP")
    e = "" if "LOGSTASH_CLIENT_ENVIRONMENT" not in env else env.str("LOGSTASH_CLIENT_ENVIRONMENT")
    if host or port is None:
        return None
    return LogstashConfig(host, port, app, e)

