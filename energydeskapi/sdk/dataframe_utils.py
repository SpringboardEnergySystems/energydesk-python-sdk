import json
from io import BytesIO
from typing import Union

import pandas as pd


def text_to_dataframe_if_not_none(value: Union[bytes, None]) -> pd.DataFrame:
    if value is not None:
        io = BytesIO(value)
        dtypes = json.loads(io.readline())
        date_columns = [key for (key, value) in dtypes.items() if str(value).startswith("date")]
        return pd.read_csv(io, parse_dates=date_columns)
    else:
        return None


def dataframe_to_text(df: pd.DataFrame) -> str:
    dtypes = df.dtypes
    dtypes_json = dtypes.apply(lambda x: x.name).to_json()
    return "\n".join([dtypes_json, df.to_csv()])