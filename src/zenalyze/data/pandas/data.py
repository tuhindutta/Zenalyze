from dataclasses import dataclass
import pandas as pd
from zenalyze.data.data_base_class import Data, DataLoad
from zenalyze.data.pandas.metadata import get_metadata


@dataclass
class PandasData(Data):
    """
    Concrete implementation of the generic `Data` container for pandas-based datasets.

    This class does not modify the behaviour of the base `Data` class, but serves as
    an explicit type marker for pandas-backed tables loaded through
    `PandasDataLoad`. The class provides a simple convenience property for
    retrieving its class name, which can be useful for logging, debugging, or
    runtime backend checks.
    """
    @property
    def get_class_name(self):
        """
        Return the class name of this pandas data wrapper.

        Returns
        -------
        str
            The literal class name `"PandasData"`.
        """
        return self.__class__.__name__


class PandasDataLoad(DataLoad):
    """
    pandas-specific implementation of the generic `DataLoad` interface.

    `PandasDataLoad` is responsible for:
    - Scanning a directory for supported tabular files.
    - Loading them into pandas DataFrames.
    - Extracting metadata using the pandas metadata utility (`get_metadata`).
    - Returning dataset wrappers compatible with the `DataLoad` base class.

    This class provides the pandas backend logic that the core framework relies on
    when operating in a pandas environment.
    """
    def __init__(self, data_loc):
        """
        Initialize the pandas data loader.

        Parameters
        ----------
        data_loc : str
            Path to the directory containing CSV/Excel files and an optional
            dataset description file. The base `DataLoad` handles discovery and
            metadata assembly, while this subclass wires in pandas-specific
            reading functions.
        """
        super().__init__(data_loc, get_metadata)

    @property
    def get_class_name(self):
        """
        Return the class name of this loader.

        Returns
        -------
        str
            The literal class name `"PandasDataLoad"`; useful for backend
            identification, logging, or debugging.
        """
        return self.__class__.__name__

    def _loader(self, path:str) -> pd.DataFrame:
        """
        Load a CSV or Excel file into a pandas DataFrame.

        Parameters
        ----------
        path : str
            Full file path to load.

        Returns
        -------
        pandas.DataFrame or None
            A DataFrame containing file contents, or `None` if the extension
            is not supported by this loader.

        Notes
        -----
        Supported formats:
        - `.csv`  → `pandas.read_csv`
        - `.xls` / `.xlsx` → `pandas.read_excel`
        """
        func = {
            'csv': pd.read_csv,
            'excel': pd.read_excel
        }
        return func.get(self._file_extn(path))


