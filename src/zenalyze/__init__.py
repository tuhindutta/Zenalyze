"""zenalyze
A lightweight, modular AI-powered data analyst assistant.

This package enables interactive data exploration, code generation,
and context-driven summarization using large language models (LLMs).

Main Features
--------------
1. **Automated Data Loading and Metadata Extraction**
   - Read tabular data (CSV/Excel) into DataFrames with descriptive metadata.
   - Store contextual details such as null percentages, data types, and sample values.

2. **Prompt Engineering Layer**
   - Builds structured prompts combining instructions, dataset metadata, and
     previous analysis history for reproducible model interaction.

3. **LLM Interfaces**
   - `Zenalyze` : The main orchestrator class combining prompt generation,
     LLM interaction, and in-context code execution.
   - `SummarizerLLM` : Compresses code-generation history into concise,
     reproducible summaries.
   - `BuddyLLM` : Context-aware assistant that answers analysis-related questions
     based on summaries and code context.

4. **Jupyter-Ready Workflow**
   - Designed to work seamlessly within notebooks.
   - Keeps conversational and code context synchronized.

Usage Example
--------------
>>> from zenalyze import create_zenalyze_object_with_env_var_and_last5_hist
>>> zen = create_zenalyze_object_with_env_var_and_last5_hist(globals(), "./data")
>>> zen.do("show total sales per region")

Maintainer
----------
Tuhin Kumar Dutta
"""

# Public package version
__version__ = "0.0.1"

# Core data/backends
from zenalyze.data import PandasData, PandasDataLoad, SparkData, SparkDataLoad

# High level orchestrator
from zenalyze.zenalyze import Zenalyze, TestZen

# Convenience quick-constructors
from zenalyze._quick_obj import (
    create_zenalyze_object_with_env_var_and_last5_hist,
    create_testzen_object_with_env_var_and_last5_hist,
)

# Chat helpers (expose at package root for convenience)
from zenalyze.chat.summarizer_llm import CodeSummarizerLLM
from zenalyze.chat.buddy_llm import BuddyLLM

__all__ = [
    "PandasData",
    "PandasDataLoad",
    "SparkData",
    "SparkDataLoad",
    "Zenalyze",
    "TestZen",
    "create_zenalyze_object_with_env_var_and_last5_hist",
    "create_testzen_object_with_env_var_and_last5_hist",
    "CodeSummarizerLLM",
    "BuddyLLM",
]
