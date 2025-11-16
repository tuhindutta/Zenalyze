from typing import Dict
import random

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def get_sample_values_from_column(df: DataFrame, count: int = 5) -> str:
    """
    For each column in a Spark DataFrame, collect up to `count` unique non-null values,
    sampling with replacement if needed. Returns a stringified dict (single quotes removed).
    Note: this function collects distinct values per column to the driver.
    """
    samples: Dict[str, list] = {}
    for col in df.columns:
        distinct_vals = (
            df.select(F.col(col))
              .where(F.col(col).isNotNull())
              .distinct()
              .rdd
              .map(lambda row: row[0])
              .collect()
        )

        if not distinct_vals:
            samples[col] = []
            continue

        if len(distinct_vals) >= count:
            chosen = random.sample(distinct_vals, count)
        else:
            chosen = [random.choice(distinct_vals) for _ in range(count)]

        samples[col] = [str(x) for x in chosen]

    return str(samples).replace("'", "")


def _null_count_for_column(df: DataFrame, column: str, col_type: str) -> int:
    """
    Return count of null-like values for the given column.
    For float/double types, counts both null and NaN.
    """
    null_count = df.filter(F.col(column).isNull()).count()

    if "double" in col_type or "float" in col_type:
        nan_count = df.filter(F.isnan(F.col(column))).count()
        null_count += nan_count

    return null_count


def get_metadata(df: DataFrame) -> str:
    """
    Generate a metadata string for a Spark DataFrame similar to your pandas version.
    Returns a string enclosed in braces.
    """
    num_rows = df.count()
    num_columns = len(df.columns)
    columns = ",".join(df.columns)

    dtypes = dict(df.dtypes)
    null_pct_map: Dict[str, str] = {}
    for c, t in dtypes.items():
        null_cnt = _null_count_for_column(df, c, t)
        pct = (100.0 * null_cnt / num_rows) if num_rows > 0 else 0.0
        null_pct_map[c] = str(pct)

    dtype_map = {c: str(t) for c, t in dtypes.items()}

    columns_sample_values = get_sample_values_from_column(df)

    columns_null_pct = str(null_pct_map).replace("'", "").replace(" ", "")
    columns_data_type = str(dtype_map).replace("'", "").replace(" ", "")

    metadata = (
        f"number of rows: {num_rows}\n"
        f"number of columns: {num_columns}\n"
        f"column names: {columns}\n"
        f"column value null percentage: {columns_null_pct}\n"
        f"column data types: {columns_data_type}\n"
        f"smaple values of the columns: {columns_sample_values}"
    )

    return "{" + metadata + "}"



# import pandas as pd

# def get_sample_values_from_column(data:pd.DataFrame, count:int=5) -> str:
#     """
#     Generate a dictionary containing random sample values from each column of a DataFrame.

#     For every column in the provided dataset, a small set of unique, non-null sample
#     values is selected and converted to strings. The result is returned as a formatted
#     string representation of the dictionary (with single quotes removed).

#     Parameters
#     ----------
#     data : pd.DataFrame
#         The input DataFrame from which sample values are to be drawn.
#     count : int, optional
#         Number of sample values to retrieve per column. Defaults to 5.

#     Returns
#     -------
#     str
#         A stringified dictionary where each key is a column name and each value
#         is a list of up to `count` unique sample values (as strings).

#     Notes
#     -----
#     - Sampling is performed with replacement to ensure `count` samples even if
#       a column has fewer unique values.
#     - The returned string can be printed or logged for quick inspection of data variety.
#     """
#     samples = {}
#     for column in data.columns:
#         lst = data[column].dropna().drop_duplicates().sample(count, replace=True).unique()
#         samples[column] = [str(i) for i in lst]

#     return str(samples).replace("'", '')

# def get_metadata(df:pd.DataFrame) -> str:
#     """
#     Generate a structured string summarizing key metadata for a given DataFrame.

#     This function extracts and compiles various descriptive statistics and structural
#     details about the input DataFrame, including dimensions, column names, null
#     percentages, data types, and sample values.

#     Parameters
#     ----------
#     df : pd.DataFrame
#         The input DataFrame for which metadata will be generated.

#     Returns
#     -------
#     str
#         A formatted string enclosed in braces `{}` containing:
#         - Total number of rows and columns.
#         - List of column names.
#         - Percentage of null values per column.
#         - Data type of each column.
#         - Random sample values per column (via `get_sample_values_from_column`).

#     Notes
#     -----
#     - The returned string is suitable for logging, descriptive summaries, or metadata
#       fields in a higher-level data container (e.g., `Data` objects).
#     - Sampling is randomized and may differ on each call.
#     - Whitespace and quotes are removed from internal dictionary string representations
#       for compact formatting.
#     """
#     num_rows = len(df)
#     num_columns = len(df.columns)
#     columns = ','.join(list(df.columns))
#     columns_null_pct = str(dict((100*df.isnull().sum()/len(df)).astype('str'))).replace("'", "").replace(' ','')
#     columns_data_type = str(dict(df.dtypes.apply(lambda x: str(x).replace('dtype(', '').replace(')', '')))).replace("'", "").replace(' ','')
#     columns_sample_values = get_sample_values_from_column(df)
#     metadata = f"""number of rows: {num_rows}
# number of columns: {num_columns}
# column names: {columns}
# column value null percentage: {columns_null_pct}
# column data types: {columns_data_type}
# smaple values of the columns: {columns_sample_values}"""
#     return '{'+metadata+'}'