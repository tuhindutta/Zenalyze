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

    metadata = {
        "number of rows": num_rows,
        "number of columns": num_columns,
        "column names": columns,
        "column value null percentage": columns_null_pct,
        "column data types": columns_data_type,
        "smaple values of the columns": columns_sample_values
    }

    return metadata

