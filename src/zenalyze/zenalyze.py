import inspect
from zenalyze.prompt import Prompt
from zenalyze.chat import LLM
from zenalyze.chat import BuddyLLM


class Zenalyze(Prompt, LLM):
    """
    High-level orchestration layer that combines prompt construction, model
    interaction, code generation, and code execution for interactive data analysis.

    This class mixes the capabilities of:
    - `Prompt`   → builds backend-aware system instructions and metadata-rich prompts,
    - `LLM`      → communicates with the primary code-generation model,
    - BuddyLLM   → provides conversational, explanatory responses (non-code).

    At initialization, all provided datasets are injected into the caller's
    `globals()` so that any generated code may directly reference them by their
    dataset variable names.

    Parameters
    ----------
    globals_dic : dict
        The caller's global namespace. All dataset variables will be added to
        this dictionary so that generated code executes in the same environment.
    *args : Data | DataLoad
        One or more dataset wrappers or dataset loaders. All datasets discovered
        by these loaders become part of the prompt context for the LLM.

    Attributes
    ----------
    args : tuple
        The raw arguments provided to the constructor.
    data : list[Data]
        Inherited from `Prompt`. Contains all dataset wrappers supplied.
    mode : str
        Inherited from `Prompt`. Indicates `"Pandas"` or `"PySpark"` backend.
    history : list[str]
        Inherited from `LLM`. Stores sequential query–response text for context.
    return_query : bool
        Determines whether `do()` returns the code string after execution.
    buddy_llm : BuddyLLM
        Helper LLM used for summarization, explanation, and non-code questions.
    """

    def __init__(self, globals_dic, *args):
        """
        Initialize both Prompt and LLM components, register datasets into the
        provided global namespace, attach the Buddy LLM, and print a summary.
        """
        Prompt.__init__(self, *args)
        LLM.__init__(self)
        self.buddy_llm = BuddyLLM()
        self.args = args
        loaded_data_names = []
        for data in self.data:
            globals_dic[data.name] = data.data
            loaded_data_names.append(data.name)
        self.return_query = True
        print(self.__repr__())

    def __repr__(self):
        """
        Return a readable summary indicating this is a Zenalyze object and
        listing all available dataset names.
        """
        txt = Prompt.__repr__(self).replace('Prompt', 'Zenalyze')
        return txt
        

    def code(self, query:str) -> str:
        """
        Generate Python code (but do not execute it) for the given natural-language query.

        Parameters
        ----------
        query : str
            The user's instruction describing a data transformation or analysis.

        Returns
        -------
        str
            The code produced by the LLM according to the backend (Pandas or PySpark),
            system instructions, metadata context, and chat history.
        """
        payload = self.get_payload(query, self.get_history)
        res = self.response(payload)
        return res

    @staticmethod
    def __gather_caller_ns(depth=2):
        """
        Capture the caller’s execution frame and build a merged namespace for safe execution.

        This constructs a combined namespace containing:
        - caller globals
        - caller locals
        - builtins

        so that LLM-generated code behaves as if the user manually wrote it in
        the same environment.

        Parameters
        ----------
        depth : int
            Number of frames to walk upward to reach the caller. Default is 2.

        Returns
        -------
        tuple[frame, dict]
            The caller frame and the merged namespace into which code will execute.
        """
        frame = inspect.currentframe()
        for _ in range(depth):
            frame = frame.f_back
        g = frame.f_globals.copy()
        l = frame.f_locals.copy()
        ns = {"__builtins__": __builtins__}
        ns.update(g)
        ns.update(l)
        return frame, ns

    def do(self, query:str, echo=True, return_namespace=False) -> str:
        """
        Generate code for the query and execute it inside the caller’s environment.

        Parameters
        ----------
        query : str
            Natural-language instruction describing the computation to perform.
        echo : bool, optional
            If True, prints the generated code before execution.
        return_namespace : bool, optional
            When True, also returns the full execution namespace.

        Returns
        -------
        str | tuple[str, dict] | None
            - Code string (if `return_query=True`)
            - `(code, namespace)` when `return_namespace=True`
            - None if `return_query=False`

        Notes
        -----
        The executed namespace is pushed back into the caller’s globals,
        ensuring variables generated inside the LLM-produced code persist after execution.
        """
        code_str = self.code(query)
        if echo:
            print(code_str)
    
        frame, ns = self.__gather_caller_ns()
        exec(code_str, ns)

        frame.f_globals.update({k: v for k, v in ns.items() if k not in ("__builtins__",)})
    
        if self.return_query:
            return (code_str, ns) if return_namespace else code_str
        

    def buddy(self, query:str) -> str:
        """
        Use the lightweight BuddyLLM to answer explanatory or insight-based questions.

        Parameters
        ----------
        query : str
            A non-code question such as “What have we done so far?” or
            “Explain the previous steps”.

        Returns
        -------
        str
            A concise assistant-style answer based on accumulated history.
        """
        response = self.buddy_llm.buddy_response(query, self.get_history)
        return response
    




class TestZen(Prompt, LLM):
    """
    A test-only version of Zenalyze that avoids real LLM calls and executes
    in a controlled dummy environment.

    TestZen behaves like Zenalyze but:
    - Uses dummy responses instead of generating real code,
    - Avoids API calls entirely,
    - Helps test the overall workflow, namespace injection, and prompt formatting.
    """
    def __init__(self, globals_dic, *args):
        """
        Initialize the prompt and dummy LLM, attach datasets to caller globals,
        and prepare a BuddyLLM in test mode.

        Parameters
        ----------
        globals_dic : dict
            The global namespace of the caller.
        *args : Data | DataLoad
            Dataset objects or loaders providing tables for context.
        """
        Prompt.__init__(self, *args)
        LLM.__init__(self, True)
        self.buddy_llm = BuddyLLM(True)
        self.args = args
        loaded_data_names = []
        for data in self.data:
            globals_dic[data.name] = data.data
            loaded_data_names.append(data.name)
        print(self.__repr__())

    def __repr__(self):
        """
        Return a concise string representation showing the attached data sources.

        Returns
        -------
        str
            A representation such as "TestZen(Data(table1), Data(table2), ...)".
        """
        txt = Prompt.__repr__(self).replace('Prompt', 'TestZen')
        return txt

    def code(self, query:str) -> str:
        """
        Produce a deterministic dummy string instead of actual Python code.

        Intended for verifying prompt construction, metadata formatting,
        and the conversation loop without incurring model costs.
        """
        payload = self.get_payload(query, self.get_history)
        res = self.response(payload)
        return res

    def do(self, query:str) -> str:
        """
        Simulate execution of code without running anything.

        Returns a string describing what *would* have been executed.
        """
        return f"""Executing {self.code(query)}"""
    
    def buddy(self, query:str) -> str:
        """
        Use the BuddyLLM in test mode to generate a dummy explanatory response.
        """
        response = self.buddy_llm.buddy_response(query, self.get_history)
        return response