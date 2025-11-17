# Zenalyze Public API Usage Guide

This section documents the public APIs exposed at the package root. These cover data loading, orchestration, and LLM-powered analytics workflows.

---

## 1. Data Backends

- ### `PandasData`
**Represents a single pandas DataFrame plus metadata.**

Usually created internally by `PandasDataLoad`, but you can also create and pass these directly into `Zenalyze`.


- ### `PandasDataLoad(data_location: str)`
Loads all CSV/Excel files from a directory as pandas DataFrames and wraps each in a PandasData object.

Usage:
```python
loader = PandasDataLoad("./data")
datasets = loader.data
```

- ### `SparkData`
**Wraps a Spark DataFrame with metadata.**

Also passable directly into `Zenalyze` if you already constructed your own Spark DataFrames.

- ### `SparkDataLoad(spark_session, data_location: str)`
Loads CSV/Excel/Parquet files using Spark and returns Spark-backed Data objects.

Usage:
```python
spark = SparkSession.builder.getOrCreate()
loader = SparkDataLoad(spark, "./data")
datasets = loader.data
```

---

## 2. High-Level Orchestrators
### `Zenalyze`

The main orchestration engine that:
- loads provided datasets into the caller’s globals()
- builds prompts using metadata + chat history
- generates Python code from natural-language queries
- executes code with full context
- provides a built-in buddy assistant (zen.buddy("..."))
- maintains and summarizes long histories internally

✔️ Accepts ANY mix of either of following:
- `PandasData` & `PandasDataLoad`
- `SparkData` & `SparkDataLoad`

And as many as you want via *args.

Example:
```python
from zenalyze import Zenalyze, PandasDataLoad, PandasData

loader = PandasDataLoad("./data")
custom_table = PandasData(df=my_df, name="mytable")

zen = Zenalyze(globals(), loader, custom_table)

zen.do("calculate total revenue")
zen.buddy("What have we done so far?")
```
This gives maximum flexibility — you can load some tables from disk and hand-craft others dynamically.
