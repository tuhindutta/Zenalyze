import pandas as pd

def get_sample_values_from_column(data:pd.DataFrame, count:int=5) -> str:
    """
    Generate a stringified dictionary containing random sample values from each column
    of a DataFrame.

    For every column in the dataset, a small set of unique non-null values is sampled,
    converted to strings, and collected into a dictionary. The function returns the
    dictionary as a string with single quotes removed.

    Parameters
    ----------
    data : pd.DataFrame
        The input DataFrame from which sample values will be drawn.
    count : int, optional
        Number of sample values to retrieve per column. Defaults to 5.

    Returns
    -------
    str
        A string representation of a mapping where each key is a column name and each
        value is a list of up to `count` sample values (as strings).

    Notes
    -----
    - Sampling is performed with replacement to ensure `count` values even when a column
      has fewer unique entries.
    - The returned value is not a dictionary object, but a stringified version suitable
      for lightweight metadata or logging.
    """
    samples = {}
    for column in data.columns:
        lst = data[column].dropna().drop_duplicates().sample(count, replace=True).unique()
        samples[column] = [str(i) for i in lst]

    return str(samples).replace("'", '')

def get_metadata(df:pd.DataFrame) -> str:
    """
    Generate a structured metadata dictionary describing key properties of a DataFrame.

    This function compiles descriptive information such as row count, column count,
    column names, null-value percentages, inferred data types, and sample values.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame for which metadata will be generated.

    Returns
    -------
    dict
        A dictionary containing:
        - "number of rows": int  
        - "number of columns": int  
        - "column names": comma-separated string of column names  
        - "column value null percentage": dict-like string of null percentages  
        - "column data types": dict-like string of dtype information  
        - "smaple values of the columns": stringified dictionary of sample values

    Notes
    -----
    - This metadata is suitable for display, summarization, or passing into LLM prompts.
    - Null percentages and data types are represented as stringified dictionaries
      for compact formatting.
    - Sample values are obtained through `get_sample_values_from_column`.
    """
    num_rows = len(df)
    num_columns = len(df.columns)
    columns = ','.join(list(df.columns))
    columns_null_pct = str(dict((100*df.isnull().sum()/len(df)).astype('str'))).replace("'", "").replace(' ','')
    columns_data_type = str(dict(df.dtypes.apply(lambda x: str(x).replace('dtype(', '').replace(')', '')))).replace("'", "").replace(' ','')
    columns_sample_values = get_sample_values_from_column(df)
    metadata = {
        "number of rows": num_rows,
        "number of columns": num_columns,
        "column names": columns,
        "column value null percentage": columns_null_pct,
        "column data types": columns_data_type,
        "smaple values of the columns": columns_sample_values
    }
    return metadata