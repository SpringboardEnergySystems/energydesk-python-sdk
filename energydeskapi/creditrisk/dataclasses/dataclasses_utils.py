from json import JSONEncoder
from datetime import date, datetime
import pandas
import numpy
class DataclassEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, (pandas.core.series.Series,pandas.core.frame.DataFrame)):
            return obj.to_dict()
        elif isinstance(obj, numpy.int64):
            return float(obj)
        print(type(obj))
def date_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S+00:00")
        except:
            pass
    return json_dict