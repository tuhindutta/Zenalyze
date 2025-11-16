"""
Convenience constructors for quickly creating Zenalyze and TestZen objects.

This module provides lightweight factory functions that:
- Automatically choose the correct data loader (pandas or Spark) based on
  whether a `SparkSession` is supplied.
- Initialize the main `Zenalyze` or `TestZen` analysis engine with the loaded
  data and the caller's global namespace.
- Configure history retention defaults for efficient summarization during LLM-
  driven analysis sessions.

These helpers are intended for simple, ergonomic creation of Zenalyze objects
inside notebooks or scripts without manually selecting data loaders.
"""

from functools import partial
from pyspark.sql import SparkSession
from zenalyze.data import PandasDataLoad, SparkDataLoad
from zenalyze.zenalyze import Zenalyze, TestZen


def create_zenalyze_object_with_env_var_and_last5_hist(globals_dic, data_location:str,
                                                       spark_session:SparkSession=None):
    """
    Create a configured `Zenalyze` instance with automatic backend selection.

    If a SparkSession is provided, a Spark-based loader is used; otherwise,
    a pandas-based loader is selected. The function:
    - Loads data from the given directory using the appropriate backend.
    - Injects loaded datasets into the caller's global namespace.
    - Initializes a `Zenalyze` instance with history retention of 5.
    - Ensures the generated code is executed but not printed by default
      (`return_query = False`).

    Parameters
    ----------
    globals_dic : dict
        The caller's globals dictionary where dataset variables will be injected.
    data_location : str
        Directory path containing input tabular files.
    spark_session : SparkSession, optional
        If supplied, enables Spark-based data loading; otherwise pandas is used.

    Returns
    -------
    Zenalyze
        A configured Zenalyze object ready for interactive analysis.
    """
    loader = partial(SparkDataLoad, spark_session) if spark_session else PandasDataLoad
    data = loader(data_location)
    zen = Zenalyze(globals_dic, data)
    zen.history_retention = 5
    zen.return_query = False
    return zen

def create_testzen_object_with_env_var_and_last5_hist(globals_dic, data_location:str,
                                                      spark_session:SparkSession=None):
    """
    Create a configured `TestZen` instance for offline or dry-run usage.

    This function mirrors `create_zenalyze_object_with_env_var_and_last5_hist`
    but initializes a `TestZen` object, which runs in test mode and does not
    call any external LLM API. It is suitable for testing pipeline behavior
    without incurring model cost.

    Parameters
    ----------
    globals_dic : dict
        The caller's globals dictionary where dataset variables will be injected.
    data_location : str
        Directory path containing input tabular files.
    spark_session : SparkSession, optional
        If provided, uses Spark for data loading; otherwise defaults to pandas.

    Returns
    -------
    TestZen
        A configured TestZen object with history retention set to 5.
    """
    loader = partial(SparkDataLoad, spark_session) if spark_session else PandasDataLoad
    data = loader(data_location)
    zent = TestZen(globals_dic, data)
    zent.history_retention = 5
    return zent