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
    available datasets, execution mode (Pandas or PySpark), and the ongoing analysis
    context.

    This class acts as the intermediary between loaded data (`Data` or `DataLoad`
    objects) and the LLM interface. It:
    - Detects whether the analysis backend is pandas or Spark.
    - Generates backend-specific instructions for code generation.
    - Embeds metadata for all loaded datasets into the system prompt.
    - Packages user queries, system instructions, and chat history into a complete
      `Payload` object.

    Parameters
    ----------
    *args : Data or DataLoad
        One or more dataset objects (`Data`) or dataset loader objects (`DataLoad`).
        The loader form may contain multiple datasets; each dataset contributes to
        the metadata used in LLM prompting.

    Attributes
    ----------
    data : list[Data]
        All datasets extracted from the provided arguments.
    mode : str
        Execution mode inferred from provided objects — either `"Pandas"` or `"PySpark"`.
    __instruction : str
        Base instruction block injected into the system prompt, including backend
        rules, coding conventions, and history-continuation rules.

    Methods
    -------
    __get_data_and_mode()
        Extracts all `Data` objects from arguments and determines whether the
        execution backend is pandas or Spark.
    __create_instructions_with_mode()
        Constructs a backend-aware instruction block containing coding rules
        and analysis-continuation constraints.
    __repr__()
        Returns a compact representation listing loaded datasets.
    format_metadata_to_required_format(data)
        Converts a single dataset’s metadata into formatted text for prompting.
    llm_formatted_metadata
        Builds a multi-dataset metadata section for inclusion in system messages.
    instructions
        Get or set the instruction block.
    get_payload(user_input, formatted_chat_history)
        Produces a `Payload` object containing system prompt, metadata, history,
        and user query for LLM submission.
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
5) Continue the analysis using the established context in chat history.
6) Add brief comments."""
        
        self.__user_prompt_intruction = """Refer the following chat history to
    - Reuse callable identifiers highlighted in backticks (`), such as tables, variables, and intermediate results; they already exist in the workspace and should be used directly.
    - Reuse column or field names highlighted in angle brackets (‹ ›); treat them as existing schema elements and reference them directly wherever needed.
        - Do not generate code to:
            - check for their presence in globals.
            - recreate or redefine them."""

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
Data file description: {data.description}
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

    @property
    def user_prompt_intruction(self):
        return self.__user_prompt_intruction
    
    @user_prompt_intruction.setter
    def user_prompt_intruction(self, value):
        self.__user_prompt_intruction = value


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
        user_instructions = self.user_prompt_intruction
        content = f"""{user_instructions}

Chat history:
{chat_history}

Query: {user_input}
"""
        txt = [{"role": "system", "content": system_prompt},
              {"role": "user", "content": content}]
        payload = {'query':user_input, 'payload_message':txt}
        return Payload(**payload)



