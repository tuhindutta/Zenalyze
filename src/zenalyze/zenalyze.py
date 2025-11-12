import inspect
from zenalyze.prompt import Prompt
from zenalyze.chat import LLM
from zenalyze.chat import BuddyLLM


class Zenalyze(Prompt, LLM):
    """
    High-level interface that combines prompt construction and LLM interaction to
    generate code from natural-language queries and (optionally) execute it in
    the caller's environment.

    On initialization, it registers provided datasets into the caller's globals
    (using the given `globals_dic`) so generated code can reference them by name.

    Parameters
    ----------
    globals_dic : dict
        The caller's globals dictionary where dataset variables will be injected.
    *args : Data | DataLoad
        One or more `Data` or `DataLoad` objects used to build prompt context.

    Attributes
    ----------
    args : tuple
        The original positional arguments supplied at construction time.
    return_query : bool
        Controls the return behavior of `do`; when True, returns the generated code
        (and optionally the namespace).
    data : list[Data]
        Inherited from `Prompt`; all datasets available to the model.
    history : list[str]
        Inherited from `LLM`; textual log of prior interactions.
    """

    def __init__(self, globals_dic, *args):
        """Initialize prompt/LLM mixin, expose datasets into `globals_dic`, and print a summary."""
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
        """Return a concise representation showing available data sources."""
        txt = Prompt.__repr__(self).replace('Prompt', 'Zenalyze')
        return txt
        

    def code(self, query:str) -> str:
        """
        Produce model-generated Python code for the given natural-language query.

        Parameters
        ----------
        query : str
            The user's request describing the desired analysis or transformation.

        Returns
        -------
        str
            Generated Python code as a string (no execution performed here).
        """
        payload = self.get_payload(query, self.get_history)
        res = self.response(payload)
        return res

    @staticmethod
    def __gather_caller_ns(depth=2):
        """
        Collect the caller's execution frame and a merged namespace.

        This inspects call frames to build a namespace that contains the caller's
        globals and locals, enabling generated code to run as if authored in the
        caller's scope.

        Parameters
        ----------
        depth : int, optional
            How many frames to step back from the current function to reach the
            intended caller. Defaults to 2.

        Returns
        -------
        tuple[frame, dict]
            A tuple of (frame, namespace) where `frame` is the caller's frame
            object and `namespace` is a dict combining globals/locals plus builtins.
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
        Generate code for a query and execute it inside the caller's scope.

        Parameters
        ----------
        query : str
            Natural-language instruction describing the desired code.
        echo : bool, optional
            If True, print the generated code before execution. Defaults to True.
        return_namespace : bool, optional
            If True, return both the code string and the execution namespace.
            Defaults to False.

        Returns
        -------
        str | tuple[str, dict] | None
            Returns the generated code string, or a tuple (code, namespace) when
            `return_namespace=True`. Returns None if `self.return_query` is False.

        Notes
        -----
        - Execution is performed via `exec` in a merged namespace gathered from
          the caller's frame; new/updated names are pushed back to the caller's
          globals for visibility after execution.
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
        response = self.buddy_llm.buddy_response(query, self.get_history)
        return response
    




class TestZen(Prompt, LLM):
    """
    Lightweight test harness for the Zenalyze workflow that uses dummy LLM responses.

    This class combines `Prompt` and `LLM` in test mode to avoid real API calls,
    injects provided datasets into a supplied globals dictionary for easy access,
    and offers simple methods to generate and (mock) execute code for a query.
    """
    def __init__(self, globals_dic, *args):
        """
        Initialize the test client, attach datasets to caller globals, and enable dummy mode.

        Parameters
        ----------
        globals_dic : dict
            The caller's globals dictionary where each dataset will be injected
            under its `Data.name`.
        *args : Data | DataLoad
            One or more `Data` or `DataLoad` instances that provide table data
            and metadata to seed the prompt context.
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
        Produce a dummy code string for the given natural-language query.

        Parameters
        ----------
        query : str
            The user's instruction describing the desired analysis or transformation.

        Returns
        -------
        str
            Model (dummy) response text intended to represent generated Python code.
        """
        payload = self.get_payload(query, self.get_history)
        res = self.response(payload)
        return res

    def do(self, query:str) -> str:
        """
        Simulate execution by returning a formatted string that includes the code.

        Parameters
        ----------
        query : str
            The user's instruction to convert into code.

        Returns
        -------
        str
            A string indicating execution along with the dummy code content.
        """
        return f"""Executing {self.code(query)}"""
    
    def buddy(self, query:str) -> str:
        response = self.buddy_llm.buddy_response(query, self.get_history)
        return response