from dataclasses import dataclass
import pandas as pd
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import SparkSession
from zenalyze.data.data_base_class import Data, DataLoad
from zenalyze.data.spark.metadata import get_metadata


@dataclass
class SparkData(Data):
    """
    Concrete `Data` wrapper for Spark-backed datasets.

    This class functions as a typed marker indicating that the underlying
    dataset is a Spark DataFrame. It inherits all behavior from the generic
    `Data` base class and adds a convenience property for retrieving the class
    name, which is useful for backend identification or logging.
    """
    @property
    def get_class_name(self):
        """
        Return the class name of this Spark data wrapper.

        Returns
        -------
        str
            The literal class name `"SparkData"`.
        """
        return self.__class__.__name__


class SparkDataLoad(DataLoad):
    """
    Spark-specific implementation of the `DataLoad` interface.

    This loader integrates PySpark into the generic loading pipeline by:
    - Accepting a `SparkSession` instance for file reading.
    - Registering Spark metadata extraction via `get_metadata`.
    - Resolving file extensions to the appropriate Spark read methods.
    
    It scans a directory for supported tabular files and loads them as Spark
    DataFrames, wrapping each into a `SparkData` object defined in the base
    class hierarchy.
    """

    def __init__(self, spark_session:SparkSession, data_loc:str):
        """
        Initialize the Spark data loader.

        Parameters
        ----------
        spark_session : SparkSession
            The active Spark session used to load data.
        data_loc : str
            Directory containing supported files (CSV, Excel, Parquet) and
            optional metadata descriptors. Discovery and metadata handling are
            performed by the base `DataLoad` implementation.
        """
        super().__init__(data_loc, get_metadata)
        self.spark_session = spark_session

    @property
    def get_class_name(self):
        """
        Return the class name of this loader.

        Returns
        -------
        str
            The literal class name `"SparkDataLoad"`.
        """
        return self.__class__.__name__

    def _loader(self, path:str) -> SparkDataFrame:
        """
        Load a CSV, Excel, or Parquet file into a Spark DataFrame.

        Parameters
        ----------
        path : str
            Full file path to load.

        Returns
        -------
        pyspark.sql.DataFrame or None
            A Spark DataFrame for supported extensions, or `None` if the
            extension is not recognized.

        Notes
        -----
        - `.csv`    → `spark.read.csv`
        - `.excel`  → `spark.read_excel` (requires appropriate Spark plugin)
        - `.parquet` → `spark.read.parquet`
        """
        func = {
            'csv': self.spark_session.read.csv,
            'excel': self.spark_session.read_excel,
            'parquet': self.spark_session.read.parquet
        }
        return func.get(self._file_extn(path))


