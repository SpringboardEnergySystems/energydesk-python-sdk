from json import JSONEncoder
from datetime import date, datetime
import pandas
import numpy
from decimal import Decimal
from base64 import b64encode, b64decode
from json import dumps, loads, JSONEncoder
import pickle
import dataclasses
class DataclassEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, (pandas.core.series.Series,pandas.core.frame.DataFrame)):
            return obj.to_dict()
        elif isinstance(obj, numpy.int64):
            return float(obj)
        elif isinstance(obj, set):   # How to serialize SETS. Different approaches; this is more readble than pickle objects
            return dict(_set_object=list(obj))
        elif dataclasses.is_dataclass(obj):
            return obj.__dict__

def as_python_object(json_dict):   # Not just date_hook anymore. Also handles parsing of sets and other types
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            pass
    if '_set_object' in json_dict:
        d=json_dict['_set_object']
        print(d)
        return set(d)
    return json_dict

def date_hook(json_dict):   # For backward compatibility
    return as_python_object(json_dict)
