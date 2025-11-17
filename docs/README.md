# 🚀 Zenalyze
**AI-powered, context-aware data analysis with Pandas or PySpark**

`zenalyze` turns Large Language Models into a practical coding assistant designed specifically for data analysis.  
It loads datasets, extracts metadata, builds intelligent prompts, tracks analysis history, and generates fully executable Python code and even executes directly in your environment.

### **[GitHub Link](https://github.com/tuhindutta/Zenalyze)**

Works seamlessly with:

- Pandas  
- PySpark  
- Jupyter Notebook  
- OpenAI-compatible chat APIs (Groq, etc.)  
- Multiple cooperating LLMs (Code LLM, Summarizer LLM, Buddy LLM)

---

## 🌟 Features Overview

### 1. Automatic Data Loading + Metadata Extraction
Effortlessly load and describe datasets through:

- `PandasDataLoad`
- `SparkDataLoad`

Supports:

- CSV  
- Excel  
- Parquet (Spark)

Extracts and formats metadata such as:

- row and column counts  
- null percentages  
- data types  
- random non-null sample values  

Metadata is automatically embedded into prompts so the LLM generates context-aware code.

---

### 2. Intelligent Prompt Engineering
Every call to `.do()` builds a complete LLM prompt with:

- backend mode (Pandas or PySpark)  
- coding rules  
- metadata for all loaded tables  
- compressed chat history  
- variable reuse rules  
- safety constraints (Python-only, no markdown)

The LLM returns procedural Python code that:

- reuses existing variables  
- avoids unnecessary imports  
- never redefines variables already created  
- executes cleanly inside your notebook

---

### 3. Zenalyze: End-to-End LLM-Powered Analysis
The main controller:

- builds prompts  
- calls the LLM  
- returns code  
- executes code in your namespace  
- injects dataframes into `globals()`  
- tracks full history  

Example:

```python
zen.do("calculate total revenue per customer")
```

---

### 3. Zenalyze: End-to-End LLM-Powered Analysis
Long analysis sessions stay manageable.
- After every N steps, the Summarizer LLM compresses history:
    - rewrites user queries concisely
    - summarizes LLM code actions
    - preserves variable names in backticks
    - keeps join keys and transformations
    - maintains consistency across steps
This allows large multi-step workflows without losing cont

---

### 4. Buddy Assistant (BuddyLLM)
A conversational assistant for explanations and walkthroughs.

Examples:

```python
zen.buddy("What have we done so far?")
zen.buddy("Explain the last transformation in simple words")
```

It reads from summarized history and replies naturally.

---

### 6. Test Mode (TestZen)
A fully offline, deterministic, API-free mode.
- no API calls
- zero cost
- afe for CI/CD
- ideal for development

Example:

```python
from zenalyze import create_testzen_object_with_env_var_and_last5_hist

zent = create_testzen_object_with_env_var_and_last5_hist(globals(), "./data")
zent.do("show me something")  # deterministic dummy output
```

---

### 7. One-Line Quick Constructors
Pandas backend

```python
from zenalyze import create_zenalyze_object_with_env_var_and_last5_hist

zen = create_zenalyze_object_with_env_var_and_last5_hist(globals(), "./data")
```

Spark backend

```python
from pyspark.sql import SparkSession
from zenalyze import create_zenalyze_object_with_env_var_and_last5_hist

spark = SparkSession.builder.getOrCreate()

zen = create_zenalyze_object_with_env_var_and_last5_hist(
    globals(),
    "./data",
    spark_session=spark
)
```

---

## 📦 Installation
From PyPI (when available)

```bash
pip install zenalyze
```

From GitHub

```bash
pip install git+https://github.com/tuhindutta/Zenalyze.git
```

---

## 📘 Basic Usage
1. Initialize

```python
from zenalyze import create_zenalyze_object_with_env_var_and_last5_hist

zen = create_zenalyze_object_with_env_var_and_last5_hist(globals(), "./data")
```

2. Run a query

```python
zen.do("show unique customers and total sales per region")
```

3. Continue analysis

```python
zen.do("plot distribution of order quantities per product")
```

4. Ask the Buddy assistant

```python
zen.buddy("Summarize steps 1 to 4")
```

---

## 📂 Project Structure
```
zenalyze/
 ├── data/
 │    ├── pandas/
 │    ├── spark/
 │    ├── data_base_class.py
 │    └── __init__.py
 │
 ├── chat/
 │    ├── llm.py
 │    ├── summarizer_llm.py
 │    ├── buddy_llm.py
 │    └── __init__.py
 │
 ├── prompt.py
 ├── zenalyze.py
 ├── _quick_obj.py
 ├── __init__.py
 └── README.md
```

---

## 🧱 Core Components
Data Layer

| Component                      | Purpose                 |
| ------------------------------ | ----------------------- |
| `Data`                     | Base dataset wrapper    |
| `PandasData`, `PandasDataLoad` | Pandas backend          |
| `SparkData`, `SparkDataLoad`   | Spark backend           |
| `metadata.py`                  | Extracts table metadata |

LLM Layer

| Component       | Purpose                               |
| --------------- | ------------------------------------- |
| `LLM`           | Primary code-generation model         |
| `SummarizerLLM` | History compression and summarization |
| `BuddyLLM`      | Natural-language assistant            |

Prompt Layer
- backend-aware instructions (Pandas or PySpark)
- rich dataset metadata (columns, dtypes, nulls, samples)
- history tracking
- variable reuse (LLM reuses names in backticks)

Execution Layer
- Zenalyze.do() performs:
- prompt construction
- code generation
- optional code printing
- execution inside user namespace
- syncing variables
- updating history

---

## 🧪 Example Workflow

```python
zen.do("give me customer count by city")
zen.do("merge customers with orders and compute order totals")
zen.do("show the top 5 highest spending customers")
zen.buddy("Explain the main insights so far")
```

---

## 🔒 Security Notes
- Raw data never leaves your environment.
- Only metadata and code snippets are shared with the LLM.
- You retain full control of execution.

---

## 👤 Maintainer
**Tuhin Kumar Dutta**

- 🌐 Website: https://www.tuhindutta.com/
- 💼 LinkedIn: https://www.linkedin.com/in/t-k-dutta

---

## ⭐ Contribute
Pull requests and issues are welcome.

```bash
git clone https://github.com/tuhindutta/Zenalyze.git
```

Let’s build the most capable AI-driven data analysis toolkit together.
