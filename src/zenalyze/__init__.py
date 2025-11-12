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
>>> from zenalyze import create_quick_zenalyze_object_with_env_var_and_last5_hist
>>> zen = create_quick_zenalyze_object_with_env_var_and_last5_hist(globals(), "./data")
>>> zen.do("show total sales per region")

Package maintained by: Tuhin Kumar Dutta 
"""

from zenalyze.data import Data, DataLoad
from zenalyze.zenalyze import Zenalyze, TestZen

def create_quick_zenalyze_object_with_env_var_and_last5_hist(globals_dic, data_location:str):
    data = DataLoad(data_location)
    zen = Zenalyze(globals_dic, data)
    zen.history_retention = 5
    zen.return_query = False
    return zen

def create_quick_testzen_object_with_env_var_and_last5_hist(globals_dic, data_location:str):
    data = DataLoad(data_location)
    zent = TestZen(globals_dic, data)
    zent.history_retention = 5
    return zent

__all__ = ["Data", "DataLoad", "Zenalyze", "TestZen",
           "create_quick_zenalyze_object_with_env_var_and_last5_hist",
           "create_quick_zenalyze_object_with_env_var_and_last5_hist"]