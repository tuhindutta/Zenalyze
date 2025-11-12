import os
from typing import Tuple
import requests


class BuddyLLM:
    """
    Lightweight conversational interface designed to assist data analysts by answering
    context-aware queries based on prior analysis summaries, code history, or insights.
    This model operates as a 'buddy' layer that provides natural-language explanations,
    suggestions, or clarifications without directly viewing raw data.

    Behaviour:
    - Uses an environment variable `BUDDY_MODEL` (defaults to `'openai/gpt-oss-20b'`)
      and an API key from `GROQ_API_KEY` when not in test mode.
    - In test mode, disables live API calls and returns a deterministic dummy message.
    - Wraps model interaction in a simple, structured prompt composed of context
      (system message) and a user query (user message).
    """
    def __init__(self, test_mode:bool = False):
        """
        Initialize the BuddyLLM instance.

        Parameters
        ----------
        test_mode : bool, optional
            If True, disables API calls and uses static test responses. Defaults to False.
        """
        self.__test_mode = test_mode
        self.__buddy_model = os.getenv("BUDDY_MODEL") or 'openai/gpt-oss-20b' if not self.__test_mode else None
        self.api_key = os.getenv("GROQ_API_KEY") if not self.__test_mode else None

    @property
    def buddy_model(self) -> str:
        """
        Get the model identifier used for Buddy queries.

        Returns
        -------
        str
            The active model name (e.g., `'openai/gpt-oss-20b'`).
        """
        return self.__buddy_model

    @buddy_model.setter
    def buddy_model(self, value:str) -> None:
        """
        Set the model identifier for Buddy queries.

        Parameters
        ----------
        value : str
            Model name or identifier to assign.
        """
        self.__buddy_model = value


    def __create_payload(self, user_input:str, context:str) -> Tuple[str, dict, dict]:
        """
        Construct the API request payload for a context-aware query.

        Parameters
        ----------
        user_input : str
            The user's natural-language query.
        context : str
            Descriptive context summarizing previous steps, code, or insights
            relevant to the current question.

        Returns
        -------
        tuple
            (headers, model_payload), where:
            - headers : dict -> HTTP headers including the authorization token.
            - model_payload : dict -> JSON body containing model name, messages, and parameters.
        """
        system_prompt = f"""You are an assistant to a data analyst.
Help to answer queries based on the following context of Python codes, steps and data insights.
You do not see the actual data for security reasons.
Context:
{context}"""

        user_prompt = f"""Keep the response concise and professional.
Query:
{user_input}"""

        message = [{"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt}]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }       
        model_payload = {
            "model": self.__buddy_model,
            "messages": message,
            "temperature": 0.3,
            # "max_tokens": 8000          
        }
        return headers, model_payload

    def __response(self, user_input:str, context:str) -> str:
        """
        Execute a live API call to generate a Buddy response.

        Parameters
        ----------
        user_input : str
            The analyst's question or request.
        context : str
            The analytical or conversational context provided to the model.

        Returns
        -------
        str
            The model's text response, or an error message if a failure occurs.
        """   
        headers, model_payload = self.__create_payload(user_input, context)

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
    
    def buddy_response(self, user_input:str, context:str) -> str:
        """
        Public method for generating a contextual assistant reply.

        Behaviour
        ---------
        - In live mode: performs an API call and returns the model's answer.
        - In test mode: skips network access and returns a static test message.

        Parameters
        ----------
        user_input : str
            The user's natural-language question or instruction.
        context : str
            Background information, prior analysis summary, or discussion context.

        Returns
        -------
        str
            The model's textual answer or a test message.
        """
        if self.__test_mode:
            res = "Buddy test PASS"
        else:
            res = self.__response(user_input, context)
        return res