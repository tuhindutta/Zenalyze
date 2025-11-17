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
- ### `Zenalyze`
    The main orchestration engine that:
    - loads provided datasets into the caller’s globals()
    - builds prompts using metadata + chat history
    - generates Python code from natural-language queries
    - executes code with full context
    - provides a built-in buddy assistant (zen.buddy("..."))
    - maintains and summarizes long histories internally

    ✔️ Accepts ANY mix of either of following:
    - `PandasData` and/or `PandasDataLoad`
    - `SparkData` and/or `SparkDataLoad`

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


- ### `TestZen`
    A mock/testing version of `Zenalyze` with:
    - no real LLM calls
    - predictable dummy responses
    - fully functional prompt logic

    ✔️ Also accepts any combination of Data/ DataLoad objects:
    ```python
    from zenalyze import TestZen, PandasDataLoad
    
    loader = PandasDataLoad("./data")
    zen = TestZen(globals(), loader)
    
    zen.do("summary stats")
    zen.buddy("What next?")
    ```

---

## 3. Convenience Constructors
- ### `create_zenalyze_object_with_env_var_and_last5_hist`

    A quick way to create a fully configured `Zenalyze` instance:
    - backend auto-detected (pandas or spark)
    - loads data from a directory
    - sets `history_retention=5`
    - sets `return_query=False` for clean `.do()` usage
    
    Usage:
    ```python
    zen = create_zenalyze_object_with_env_var_and_last5_hist(
        globals(),
        "./data"
    )
    ```

- ### `create_testzen_object_with_env_var_and_last5_hist`
    Same as above, but returns a TestZen instance.

---

## 4. Chat Helpers
- ### `CodeSummarizerLLM`

    Internal summarizer used by `Zenalyze` to compress long histories.
    Still available for direct use if needed.
    
    Usage:
    ```python
    summ = CodeSummarizerLLM()
    summary = summ.summarize(raw_history_text)
    ```

- ### `BuddyLLM`
    The assistant that powers:
    ```python
    zen.buddy("my question")
    ```
    
    You rarely need to instantiate this manually because `Zenalyze` already contains:
    ```python
    zen.buddy_llm
    ```
    
    But optional standalone use is allowed.

---

## ✔️ Final Summary

| API                                                  | Accepts What                                                            | Purpose                                |
| ---------------------------------------------------- | ---------------------------------------------------------------------   | -------------------------------------- |
| `PandasData`                                         | Individual pandas DataFrames                                            | Manual creation of Data objects        |
| `PandasDataLoad`                                     | Directory path                                                          | Load multiple pandas tables + metadata |
| `SparkData`                                          | Spark DataFrames                                                        | Manual creation of Spark Data objects  |
| `SparkDataLoad`                                      | SparkSession + directory                                                | Load Spark-backed tables + metadata    |
| **`Zenalyze`**                                       | **Any mix of either Pandas or Spark DataLoad + Data objects (`*args`)** | Main LLM analysis engine               |
| **`TestZen`**                                        | **Any mix of either Pandas or Spark DataLoad + Data objects (`*args`)** | Mock testing engine                    |
| `create_zenalyze_object_with_env_var_and_last5_hist` | Directory, SparkSession for Spark usage                                 | Quick Zenalyze setup                   |
| `create_testzen_object_with_env_var_and_last5_hist`  | Directory                                                               | Quick TestZen setup                    |
| `CodeSummarizerLLM`                                  | Raw history                                                             | Summarization utility                  |
| `BuddyLLM`                                           | Summary context                                                         | Q&A assistant                          |

