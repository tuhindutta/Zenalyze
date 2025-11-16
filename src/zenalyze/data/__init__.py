"""
zenalyze.data
=============

Data abstraction and backend-specific loaders for the zenalyze framework.

This sub-package defines the common data interface (`Data`) and provides
implementations for working with different execution backends:

Backends
--------
- `PandasData` / `PandasDataLoad`
    Data wrappers and directory-based loaders for pandas DataFrames.
    Supports CSV and Excel ingestion, along with pandas-specific metadata
    extraction utilities.

- `SparkData` / `SparkDataLoad`
    Data wrappers and directory-based loaders for Spark DataFrames.
    Supports CSV, Excel (via Spark plugins), and Parquet ingestion, along with
    Spark-specific metadata extraction utilities.

Purpose
-------
These classes unify the representation of datasets inside zenalyze, allowing
the rest of the framework (prompt building, LLM-assisted analysis, metadata
summaries) to operate agnostically across backends.

Exports
-------
- Data
- PandasData
- PandasDataLoad
- SparkData
- SparkDataLoad
"""


from zenalyze.data.data_base_class import Data
from zenalyze.data.pandas.data import PandasData, PandasDataLoad
from zenalyze.data.spark.data import SparkData, SparkDataLoad

__all__ = ['Data', 'PandasData', 'PandasDataLoad', 'SparkData', 'SparkDataLoad']