import os
from typing import Tuple
import requests


class CodeSummarizerLLM:
    """
    Lightweight wrapper for calling a summarization LLM (e.g., an OSS chat model)
    to compress and normalize code-generation history into concise, reproducible
    narrative steps.

    Behaviour:
    - Uses an environment-configured summarizer model (`SUMMARIZER_MODEL`) and
      API key (`GROQ_API_KEY`) when not in test mode.
    - In test mode, avoids external calls and returns a deterministic test string.
    - Formats a system + user prompt that instructs the model to produce
      concise stepwise summaries that preserve variable/table/column identifiers.

    Notes:
    - This class focuses only on building the payload and returning text;
      it does not parse or validate the model output.
    """

    def __init__(self, test_mode:bool = False):
        """
        Initialize the SummarizerLLM.

        Parameters
        ----------
        test_mode : bool, optional
            When True, disables live API calls and sets internal model/key to None.
            Defaults to False.
        """
        self.__test_mode = test_mode
        self.__summarizer_model = os.getenv("SUMMARIZER_MODEL") or 'openai/gpt-oss-120b' if not self.__test_mode else None
        self.api_key = os.getenv("GROQ_API_KEY") if not self.__test_mode else None

    @property
    def summarizer_model(self) -> str:
        """
        Get the model identifier used for summarization requests.

        Returns
        -------
        str
            The model name or identifier (e.g., 'openai/gpt-oss-120b').
        """
        return self.__summarizer_model

    @summarizer_model.setter
    def summarizer_model(self, value:str) -> None:
        """
        Set the model identifier used for summarization requests.

        Parameters
        ----------
        value : str
            Model identifier to use for subsequent requests.
        """
        self.__summarizer_model = value


    def __create_payload(self, user_input:str) -> Tuple[str, dict, dict]:
        """
        Build HTTP headers and the JSON payload for the chat-completions API.

        Parameters
        ----------
        user_input : str
            The raw history text to be summarized; this is embedded into the
            user message portion of the chat payload.

        Returns
        -------
        tuple
            A tuple `(headers, model_payload)` where:
            - headers : dict -> HTTP headers including Authorization.
            - model_payload : dict -> JSON body with model, messages, and params.
        """
        system_prompt = """You summarize Python data-analysis code histories so they can be quickly understood or reconstructed.

Input: each entry contains a user query and the code generated for it.

Summarize briefly what each step did, keeping:
- Exact variable names and dataset names.
- Column names or keys used in joins, groupbys, filters, selections, or renames.
- Important computations, aggregations, or plots.
- Do not summarize if the entry is already a text-only summary.
- Highlight all callable identifiers (tables, variables, DataFrame names, functions) using backticks (`).
- Highlight all field or column names using angle brackets (e.g., ‹column_name›).
- Never include code, pseudocode, or commentary.  
- Never invent identifiers; if something is unknown, write “unknown”.

Output concise step-wise sentences that explicitly state which variables were created, modified, or used, so the LLM can reliably reuse them in future steps.

Avoid code formatting or long explanations—just describe the action precisely enough that the code could be recreated from the description."""

        user_prompt = f"""Summarize the following code-generation history.
Rewrite each step as:
[Q: <brief rewritten intent>] <concise description of what the code did>

History:
{user_input}"""

        message = [{"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt}]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }       
        model_payload = {
            "model": self.__summarizer_model,
            "messages": message,
            "temperature": 0.3,
            # "max_tokens": 8000          
        }
        return headers, model_payload

    def __response(self, user_input:str) -> str:
        """
        Perform the HTTP POST to the chat-completions endpoint and return the
        model's textual response.

        Parameters
        ----------
        user_input : str
            Raw history text to summarize (passed through to __create_payload).

        Returns
        -------
        str
            The summarization text returned by the remote model, or an error
            message string if the API call failed.
        """
        headers, model_payload = self.__create_payload(user_input)

        url = "https://api.groq.com/openai/v1/chat/completions"
        try:
            response = requests.post(url, headers=headers, json=model_payload)
            api_output = response.json()
            if "error" in api_output:
                output = f"⚠️ API Error: {api_output['error'].get('message', 'Unknown error')}"
            else:
                output = api_output['choices'][0]['message']['content'].strip()
        except Exception as e:
            output = "⚠️ Some technical error occurred at my end. Please try after sometime."
            print(e)
        return output
    
    def summarize(self, user_input:str) -> str:
        """
        Public method to summarize a code-generation history string.

        Behaviour
        ---------
        - If `test_mode` is True, returns a deterministic test confirmation string.
        - Otherwise, calls the remote summarization endpoint and returns the text.

        Parameters
        ----------
        user_input : str
            The code-generation history that should be summarized.

        Returns
        -------
        str
            The model-produced summary or a test-mode placeholder.
        """
        if self.__test_mode:
            res = "History summarizer test PASS"
        else:
            res = self.__response(user_input)
        return res