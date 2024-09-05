from datetime import datetime
from unittest import TestCase
import pandas as pd
from pandas import Timestamp

from energydeskapi.sdk.dataframe_utils import dataframe_to_text, text_to_dataframe_if_not_none


class TestDataFrameUtils(TestCase):
    def test_dataframe_to_text(self):
        # Create the pandas DataFrame
        df = pd.DataFrame( [['tom', 10, datetime(2024, 10, 1)], ['nick', 15, datetime(2021, 5, 4)], ['juli', 14, datetime(2024, 10, 1)]], columns=['Name', 'Age', "Birthday"])
        text = dataframe_to_text(df)
        df2 = text_to_dataframe_if_not_none(text.encode())
        self.assertEqual("tom", df2["Name"][0])
        self.assertEqual(10, df2["Age"][0])
        self.assertEqual(Timestamp('2024-10-01 00:00:00'), df2["Birthday"][0])
