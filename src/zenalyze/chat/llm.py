import os
from typing import Tuple
import requests
from zenalyze.prompt import Payload
from zenalyze.chat.summarizer_llm import CodeSummarizerLLM


class LLM:

    """
    Lightweight wrapper for interacting with a chat-completions API (Groq-compatible),
    maintaining simple conversation history and providing test/dummy mode.

    Parameters
    ----------
    test_mode : bool, optional
        If True, disables external API calls and returns deterministic dummy responses.
        Defaults to False.

    Attributes
    ----------
    history : list[str]
        Stored turn-by-turn conversation history in a simple text format.
    history_retention : int
        Maximum number of history entries to retain; if None, retain all.
    """

    def __init__(self, test_mode:bool = False):
        """Initialize client configuration, credentials, and history containers."""
        self.__test_mode = test_mode
        self.history = []
        self.history_retention = 8
        self.summarizer = CodeSummarizerLLM()
        self.__model = os.getenv("MODEL") or 'openai/gpt-oss-120b' if not self.__test_mode else None
        self.api_key = os.getenv("GROQ_API_KEY") if not self.__test_mode else None

    @property
    def model(self) -> str:
        """str: The model identifier used for completions (read/write via property setter)."""
        return self.__model 

    @model.setter
    def model(self, value:str) -> None:
        """Return the current API key (getter intentionally non-functional in this version)."""
        self.__model = value

    @staticmethod
    def history_format(query:str, response:str) -> str:
        """
        Build a single history entry combining the query and response.

        Parameters
        ----------
        query : str
            The user query or prompt.
        response : str
            The model-generated response.

        Returns
        -------
        str
            Formatted multi-line string for history storage.
        """
        formatted_txt = f"""----------------------------
{query}
Response:
{response}
----------------------------"""
        return formatted_txt
    

    # def summarize_history(self) -> None:
    #     retn = self.history_retention
    #     hist = self.history
    #     if len(hist) == retn:
    #         compressed_hist = self.summarizer.summarize(self.get_history)
    #         self.history = [compressed_hist]


    def summarize_history(self) -> None:
        """
        Compress the accumulated analysis history using the Summarizer LLM.

        This method triggers when the number of history entries exceeds
        the configured retention limit. It selects the appropriate portion of the
        history, concatenates it into a single text block, sends it to the
        Summarizer LLM, and replaces the history buffer with the compressed result.
        """
        retn = self.history_retention
        hist = self.history
        if len(hist) > retn:

            first_non_summarized_index = 0
            for idx, h in enumerate(hist):
                if not h.startswith('[Q:'):
                    first_non_summarized_index = idx
                    break

            hist_to_compress = hist[first_non_summarized_index:]
            self.history = self.history[:first_non_summarized_index]

            stringed_history = '\n\n'.join(hist_to_compress)
            compressed_hist = self.summarizer.summarize(stringed_history)
            self.history.append(compressed_hist)


    def store_history(self, query:str, response:str) -> None:
        """
        Append a formatted entry to history while enforcing retention, if configured.

        Parameters
        ----------
        query : str
            The user query or prompt.
        response : str
            The model-generated response.
        """
        text = self.history_format(query, response)
        self.summarize_history()
        self.history.append(text)

    @property
    def get_history(self) -> str:
        """
        str: The entire conversation history concatenated with blank-line separators.
        """
        text = '\n\n'.join(self.history)
        return text

    def create_payload(self, payload:Payload) -> Tuple[str, dict, dict]:
        """
        Construct the HTTP headers and JSON body for a chat-completions request.

        Parameters
        ----------
        payload : Payload
            Object containing the user query and message list for the API.

        Returns
        -------
        tuple[str, dict, dict]
            A tuple of (query, headers, model_payload) ready for an HTTP POST.
        """
        query = payload.query
        payload_message = payload.payload_message
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }       
        model_payload = {
            "model": self.model,
            "messages": payload_message,
            "temperature": 0.3,
            # "max_tokens": 8000          
        }
        return query, headers, model_payload

    def actual_response(self, payload:Payload) -> str:
        """
        Execute a live API call to retrieve a model response and update history.

        Parameters
        ----------
        payload : Payload
            Object containing the user query and message list.

        Returns
        -------
        str
            The model response text, normalized for line breaks.
        """         
        query, headers, model_payload = self.create_payload(payload)

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
        self.store_history(query, output)
        return '\n'.join(output.split('\n'))


    def dummy_response(self, payload:Payload) -> str:
        """
        Produce a deterministic placeholder response without calling the API,
        and update history accordingly.

        Parameters
        ----------
        payload : Payload
            Object containing the user query and message list.

        Returns
        -------
        str
            A formatted dummy output string derived from the query.
        """
        query, _, _ = self.create_payload(payload)
        
        output = f"Output for ${query}$"
        self.store_history(query, output)
        return output


    def response(self, payload:Payload) -> str:
        """
        Dispatch to either the live API call or the dummy responder based on `test_mode`.

        Parameters
        ----------
        payload : Payload
            Object containing the user query and message list.

        Returns
        -------
        str
            Model output (live) or dummy output (test mode).
        """
        return self.dummy_response(payload) if self.__test_mode else self.actual_response(payload)
