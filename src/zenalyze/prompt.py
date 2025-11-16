from datetime import datetime
from pydantic import BaseModel
from typing import List
from zenalyze.data import Data
from zenalyze.data.data_base_class import DataLoad


class Payload(BaseModel):
    """
    Represents the structured payload used for communication with the LLM API.

    This model encapsulates the user's query and the formatted message list that will
    be passed to the language model endpoint for inference.

    Attributes
    ----------
    query : str
        The raw user query or instruction intended for the language model.
    payload_message : List[dict]
        A list of message dictionaries following the chat-completion format, where
        each dictionary typically includes fields such as 'role' (e.g., 'user', 'assistant')
        and 'content' (the corresponding message text).

    Notes
    -----
    This class extends `pydantic.BaseModel`, providing automatic data validation
    and type enforcement for consistent payload construction before API calls.
    """
    query: str
    payload_message: List[dict]



class Prompt:
    """
    Builds structured prompt payloads for large language model (LLM) queries based on
    available datasets and analysis context.

    This class acts as the intermediary between loaded data (`Data` or `DataLoad` objects)
    and the LLM interface by preparing well-formatted system and user messages, as well as
    metadata-rich context descriptions.

    Parameters
    ----------
    *args : Data or DataLoad
        One or more `Data` or `DataLoad` objects containing preloaded datasets and
        their associated metadata. These are used to automatically generate the
        metadata section of the prompt.

    Attributes
    ----------
    data : list[Data]
        A list of `Data` objects used as input context for the model.
    __instruction : str
        The base instruction text defining coding style and behavior rules for the model.

    Methods
    -------
    __create_instructions_with_mode() -> None
        Initializes the default instruction prompt with standardized coding guidelines.
    __repr__() -> str
        Returns a concise class representation showing associated data names.
    format_metadata_to_required_format(data: Data) -> str
        Converts a `Data` object’s attributes into a structured text block.
    llm_formatted_metadata : str
        Property that combines formatted metadata for all loaded tables into one text section.
    instructions : str
        Getter/setter property for customizing the instruction text used in system prompts.
    get_payload(user_input: str, formatted_chat_history: str) -> Payload
        Constructs a `Payload` object combining system instructions, data metadata, chat history,
        and user input for LLM query execution.
    """
    def __init__(self, *args):    
        """Initialize the prompt with one or more Data or DataLoad objects."""
        self.args = args  
        self.__get_data_and_mode()
        self.__create_instructions_with_mode()


    def __get_data_and_mode(self):
        data = []
        modes_map = {
            'PandasData': 'Pandas',
            'PandasDataLoad': 'Pandas',
            'SparkData': 'PySpark',
            'SparkDataLoad': 'PySpark'
        }

        modes = []
        for i in self.args:
            if isinstance(i, DataLoad):
                data.extend(i.data)
            elif isinstance(i, Data):
                data.append(i)
            else:
                raise ValueError('Data is not of type Data or DataLoad')           
            modes.append(modes_map.get(i.get_class_name))
            
        assert len(set(modes)) == 1, "Data mode should be either Pandas or Spark."
        self.mode = list(set(modes))[0]
        self.data = data


    def __create_instructions_with_mode(self) -> None:
        """
        Create the default base instruction string that defines how the LLM
        should generate code and display output.
        """
        mode_prompt = {
            "Pandas": "Use Pandas for data manipulation and transformation.",
            "PySpark": "Use `spark` as spark session and use sparkcontext from inside the spark session for data manipulation and transformation."
        }
        self.__instruction = f"""{datetime.today().strftime("%d %b, %Y (%A)")} - You are an expert data analyst and a coding assistant.
Write clean procedural Python code (minimum and relevant functions/classes only if extremely required) primarily using:
pandas (pd), numpy (np), matplotlib.pyplot (plt), PySpark

Rules:
1) {mode_prompt[self.mode]}
2) Tables are pre-loaded; use their names directly.
3) The packages (pd, np, plt, pyspark) are already imported—do not reimport. Import extras only if essential.
4) Output only executable Python code only (no markdown/text).
   Display only relevant data: key results, head() samples, and show plots with plt.show().
5) Continue the analysis using the established context in chat history - use the variables, column names, and keys highlighted inside backticks (`) wherever required; they already exist in the workspace. Do not:
   - check for their presence.
   - recreate or redefine them.
6) Add brief comments."""

    def __repr__(self):
        """Return a string representation listing all associated data objects."""
        args = ', '.join([f"Data({i.name})" for i in self.data])
        cls_repr = f"Prompt({args})"
        return cls_repr
    
    @staticmethod
    def format_metadata_to_required_format(data:Data) -> str:
        """
        Convert an individual `Data` object’s information into a formatted text block.

        Parameters
        ----------
        data : Data
            The dataset object to format.

        Returns
        -------
        str
            Structured text describing the table’s name, data description, column
            details, and computed metadata.
        """
        text = f"""Table name: {data.name}
Data description: {data.data_desc}
Data columns description: {data.column_desc}
Metadata: {data.metadata}"""
        return text

    @property
    def llm_formatted_metadata(self) -> str:
        """
        str: Combined metadata section describing all available datasets, formatted
        for inclusion in LLM system prompts.
        """
        texts = [self.format_metadata_to_required_format(i) for i in self.data]
        formatted_text = f'**Details of {len(texts)} tables available**:\n\n'+'\n\n'.join(texts)
        return formatted_text

    @property
    def instructions(self) -> str:
        """str: Get or set the main instruction text that defines LLM behavior."""
        return self.__instruction

    @instructions.setter
    def instructions(self, instr:str) -> None:
        """Update the instruction text with a custom value."""
        self.__instruction = str(instr)

    def get_payload(self, user_input:str, formatted_chat_history:str) -> Payload:
        """
        Build a complete prompt payload combining system instructions, dataset
        metadata, conversation history, and the current user query.

        Parameters
        ----------
        user_input : str
            The user's current query or instruction for the LLM.
        formatted_chat_history : str
            Text-formatted conversation history to maintain context continuity.

        Returns
        -------
        Payload
            A validated Payload object containing the structured query and formatted
            messages ready for API submission.
        """
        system_prompt = f"{self.instructions}\n\n{self.llm_formatted_metadata}"
        chat_history = "\n\n"+formatted_chat_history if formatted_chat_history != '' else " None"
        user_input = f"Time {datetime.today().strftime('%H:%M')} - User query: {user_input}"
        txt = [{"role": "system", "content": system_prompt},
              {"role": "user", "content": f"Chat history:{chat_history}\n\n{user_input}"}]
        payload = {'query':user_input, 'payload_message':txt}
        return Payload(**payload)



# class Prompt:

#     """
#     mode = 'pandas' or 'spark'
#     """

#     def __init__(self, *args):        
#         data = []
#         for i in args:
#             if isinstance(i, DataLoad):
#                 data.extend(i.data)
#             elif isinstance(i, Data):
#                 data.append(i)
#             else:
#                 raise ValueError('Data is not of type Data or DataLoad')
#         self.data = data
#         self.__mode = 'pandas'
#         self.__create_instructions_with_mode(self.__mode)

#     @property
#     def mode(self):
#         return self.__mode

#     @mode.setter
#     def mode(self, value:str):
#         assert value in ['pandas', 'spark'], f"value should be either 'pandas' or 'spark'"
#         self.__mode = value
#         self.__create_instructions_with_mode(self.__mode)

#     def __create_instructions_with_mode(self, mode:str):
#         self.__instruction = f"""{datetime.today().strftime("%d %b, %Y (%A)")} - You are an expert data analyst.
# MODE: {mode}
# Write clean procedural Python code (no functions/classes) using pyspark.sql, pandas (pd), numpy (np), and matplotlib.pyplot (plt).
# Rules:
# 1) Use {mode} for all data manipulation. 
# 2) Do NOT convert between Spark and pandas unless the query explicitly says “convert”. 
#    - Forbidden unless asked: toPandas(), createDataFrame, to_spark(), spark.createDataFrame, koalas, etc.
# 3) If MODE=pandas: do not reference 'spark' or pyspark APIs.
#    If MODE=spark: use SparkSession 'spark'; do not use 'sc' directly (use spark.sparkContext if needed).
# 4) Tables are pre-loaded in the requested library; use their names directly.
# 5) The packages (pd, np, plt, and pyspark) are already imported—do not reimport. Import extras only if essential.
# 6) Output only executable Python code (no markdown/text). 
#    Display only relevant data: key results, head() samples, and show plots with plt.show().
# 7) Add brief comments."""

#     def __repr__(self):
#         args = ', '.join([f"Data({i.name})" for i in self.data])
#         cls_repr = f"Prompt({args})"
#         return cls_repr

#     @property
#     def llm_formatted_metadata(self):
#         text_format = lambda d: f"""Table name: {d.name}
# Data description: {d.data_desc}
# Data columns description: {d.column_desc}
# Metadata: {d.metadata}"""
#         texts = [text_format(i) for i in self.data]
#         formatted_text = f'**Details of {len(texts)} tables available**:\n\n'+'\n\n'.join(texts)
#         return formatted_text

#     @property
#     def instructions(self):
#         return self.__instruction

#     @instructions.setter
#     def instructions(self, instr:str):
#         self.__instruction = str(instr)

#     def get_payload(self, user_input:str, formatted_chat_history:str) -> Payload:
#         system_prompt = f"{self.instructions}\n\n{self.llm_formatted_metadata}"
#         chat_history = "\n\n"+formatted_chat_history if formatted_chat_history != '' else " None"
#         user_input = f"Time {datetime.today().strftime('%H:%M')} - User query: {user_input}"
#         txt = [{"role": "system", "content": system_prompt},
#               {"role": "user", "content": f"Chat history:{chat_history}\n\n{user_input}"}]
#         payload = {'query':user_input, 'payload_message':txt}
#         return Payload(**payload)