from typing import Dict
import random

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def get_sample_values_from_column(df: DataFrame, count: int = 5) -> str:
    """
    Collect sample values for each column in a Spark DataFrame.

    For each column, this function:
    - selects distinct non-null values,
    - collects them to the driver,
    - chooses up to `count` values (sampling without replacement when possible,
      otherwise sampling with replacement),
    - converts values to strings and returns a stringified mapping (single quotes removed).

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Input Spark DataFrame to sample from.
    count : int, optional
        Number of sample values to return per column. Defaults to 5.

    Returns
    -------
    str
        A string representation of a dict mapping column names to lists of
        sample values (values converted to strings). Single quotes are removed
        for compactness.

    Notes
    -----
    - This function collects distinct values to the driver; avoid using it on
      very high-cardinality columns or massive datasets without caution.
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
    Compute the number of null-like entries in a column.

    This function counts SQL NULLs for any column. For floating columns (types
    containing 'double' or 'float'), it also counts NaN values.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        The DataFrame containing the column.
    column : str
        Column name to inspect.
    col_type : str
        String representation of the column type (as returned by `df.dtypes`).

    Returns
    -------
    int
        The count of null-like entries (NULL and, for floats, NaN) in the column.
    """
    null_count = df.filter(F.col(column).isNull()).count()

    if "double" in col_type or "float" in col_type:
        nan_count = df.filter(F.isnan(F.col(column))).count()
        null_count += nan_count

    return null_count


def get_metadata(df: DataFrame) -> str:
    """
    Generate a compact metadata mapping for a Spark DataFrame.

    The metadata includes:
    - number of rows and columns,
    - a comma-separated string of column names,
    - per-column null percentages (as stringified values),
    - per-column data types (stringified),
    - sample values per column (stringified mapping produced by
      `get_sample_values_from_column`).

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        The DataFrame to profile.

    Returns
    -------
    dict
        A dictionary with keys:
        - "number of rows": int
        - "number of columns": int
        - "column names": str (comma-separated)
        - "column value null percentage": str (stringified dict of percentages)
        - "column data types": str (stringified dict of dtypes)
        - "smaple values of the columns": str (stringified dict of sample lists)

    Notes
    -----
    - The function returns Python native collections (a dict); some fields inside
      are stringified dicts to keep the overall metadata compact for embedding in
      prompts or logs.
    - Counting and sampling operations may be expensive on very large DataFrames.
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

