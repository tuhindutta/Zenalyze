from dataclasses import dataclass
import pandas as pd
from pyspark.sql import DataFrame as SparkDataFrame
from zenalyze.data.data_base_class import Data, DataLoad
from zenalyze.data.spark.metadata import get_metadata


@dataclass
class SparkData(Data):
    @property
    def get_class_name(self):
        return self.__class__.__name__


class SparkDataLoad(DataLoad):

    def __init__(self, spark_session, data_loc):
        super().__init__(data_loc, get_metadata)
        self.spark_session = spark_session

    @property
    def get_class_name(self):
        return self.__class__.__name__

    def _loader(self, path:str) -> SparkDataFrame:
        func = {
            'csv': self.spark_session.read.csv,
            'excel': self.spark_session.read_excel,
            'parquet': self.spark_session.read.parquet
        }
        return func.get(self._file_extn(path))


