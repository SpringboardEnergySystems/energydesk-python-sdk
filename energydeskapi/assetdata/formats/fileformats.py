from enum import Enum
import logging
import os
import importlib


class FileFormatEnum(Enum):
    ELHUB = "EØHUB CSV"
    POWERSITE = "POWERSITE EVINY CSV"

def get_parser(ftype:FileFormatEnum):
    package=""
    for c in __name__.split(".")[:-1]:
        package=package + c + "."
    pname =package + "parsers." + ftype.name.lower()
    dispmodule = importlib.import_module(pname)
    dispmethod = getattr(dispmodule, "parse_timeseries")
    return dispmethod
