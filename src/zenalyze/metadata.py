import pandas as pd

def get_sample_values_from_column(data:pd.DataFrame, count:int=5) -> str:
    """
    Generate a dictionary containing random sample values from each column of a DataFrame.

    For every column in the provided dataset, a small set of unique, non-null sample
    values is selected and converted to strings. The result is returned as a formatted
    string representation of the dictionary (with single quotes removed).

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame from which sample values are to be drawn.
    count : int, optional
        Number of sample values to retrieve per column. Defaults to 5.

    Returns
    -------
    str
        A stringified dictionary where each key is a column name and each value
        is a list of up to `count` unique sample values (as strings).

    Notes
    -----
    - Sampling is performed with replacement to ensure `count` samples even if
      a column has fewer unique values.
    - The returned string can be printed or logged for quick inspection of data variety.
    """
    samples = {}
    for column in data.columns:
        lst = data[column].dropna().drop_duplicates().sample(count, replace=True).unique()
        samples[column] = [str(i) for i in lst]

    return str(samples).replace("'", '')

def get_metadata(df:pd.DataFrame) -> str:
    """
    Generate a structured string summarizing key metadata for a given DataFrame.

    This function extracts and compiles various descriptive statistics and structural
    details about the input DataFrame, including dimensions, column names, null
    percentages, data types, and sample values.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame for which metadata will be generated.

    Returns
    -------
    str
        A formatted string enclosed in braces `{}` containing:
        - Total number of rows and columns.
        - List of column names.
        - Percentage of null values per column.
        - Data type of each column.
        - Random sample values per column (via `get_sample_values_from_column`).

    Notes
    -----
    - The returned string is suitable for logging, descriptive summaries, or metadata
      fields in a higher-level data container (e.g., `Data` objects).
    - Sampling is randomized and may differ on each call.
    - Whitespace and quotes are removed from internal dictionary string representations
      for compact formatting.
    """
    num_rows = len(df)
    num_columns = len(df.columns)
    columns = ','.join(list(df.columns))
    columns_null_pct = str(dict((100*df.isnull().sum()/len(df)).astype('str'))).replace("'", "").replace(' ','')
    columns_data_type = str(dict(df.dtypes.apply(lambda x: str(x).replace('dtype(', '').replace(')', '')))).replace("'", "").replace(' ','')
    columns_sample_values = get_sample_values_from_column(df)
    metadata = f"""number of rows: {num_rows}
number of columns: {num_columns}
column names: {columns}
column value null percentage: {columns_null_pct}
column data types: {columns_data_type}
smaple values of the columns: {columns_sample_values}"""
    return '{'+metadata+'}'