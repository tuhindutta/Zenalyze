from functools import partial
from pyspark.sql import SparkSession
from zenalyze.data import PandasDataLoad, SparkDataLoad
from zenalyze.zenalyze import Zenalyze, TestZen


def create_zenalyze_object_with_env_var_and_last5_hist(globals_dic, data_location:str,
                                                       spark_session:SparkSession=None):
    loader = partial(SparkDataLoad, spark_session) if spark_session else PandasDataLoad
    data = loader(data_location)
    zen = Zenalyze(globals_dic, data)
    zen.history_retention = 5
    zen.return_query = False
    return zen

def create_testzen_object_with_env_var_and_last5_hist(globals_dic, data_location:str,
                                                      spark_session:SparkSession=None):
    loader = partial(SparkDataLoad, spark_session) if spark_session else PandasDataLoad
    data = loader(data_location)
    zent = TestZen(globals_dic, data)
    zent.history_retention = 5
    return zent