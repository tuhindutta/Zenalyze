import pandas as pd
import os
import json
from dataclasses import dataclass
import ast
from zenalyze.metadata import get_metadata


@dataclass
class Data:
    """
    Represents a dataset along with its descriptive and metadata information.

    Attributes
    ----------
    data : pd.DataFrame
        The actual dataset stored as a pandas DataFrame.
    name : str
        The identifier or variable name associated with the dataset.
    data_desc : str, optional
        A textual description of the dataset, providing context such as its purpose or origin.
    column_desc : str, optional
        A description of the dataset's columns, explaining their meaning or expected content.
    metadata : str, optional
        Additional metadata or auxiliary information related to the dataset (e.g., source, version, notes).
    """
    data: pd.DataFrame
    name: str
    data_desc: str = None
    column_desc: str = None
    metadata: str = None



_data_description_json_format = """{
    "table1": {
        "data_desc": "description of table 1",
        "columns_desc": {
            "col1": "col1 definition",
            "col2": "col2 definition"
        }
    },

    "table2": {
        "data_desc": "description of table 2",
        "columns_desc": {
            "col1": "col1 definition",
            "col2": "col2 definition"
        }
    }
}"""

class DataLoad:

    """
    Handles the loading and description management of tabular data files (CSV/Excel)
    within a specified directory.

    This class automates reading multiple datasets, retrieving or creating their
    descriptive metadata, and wrapping each dataset into a `Data` object that
    includes the loaded data and contextual descriptions.

    Parameters
    ----------
    data_loc : str
        Path to the directory containing data files and an optional 'desc.json'
        description file.

    Attributes
    ----------
    __data_paths : list of str
        Absolute paths of all data files (excluding JSON files) found in the directory.
    __data_desc_path : str
        Absolute path to the 'desc.json' file that holds dataset descriptions.
    __data_description_json_format : dict
        Template or schema describing the expected format of the description JSON.
    __description : dict or None
        Parsed JSON content from the description file, if available.
    data : list of Data
        A list of `Data` objects representing all loaded datasets.

    Methods
    -------
    __csv_or_excel(path: str) -> str
        Determines whether a file is CSV or Excel based on its extension.

    data_description_json_template : property
        Getter and setter for the internal JSON template string used to generate the description file.

    create_decription_template_file(forced: bool = False) -> None
        Creates a new `desc.json` file from the internal JSON template. Overwrites existing
        file if `forced=True`.

    __load_description() -> None
        Loads and parses the existing `desc.json` file if present.

    __loader(path: str) -> Callable
        Returns the appropriate pandas loader function (read_csv or read_excel) for the given path.

    __file_name(path: str) -> str
        Extracts and returns the base file name (without extension) from a file path.

    load_data(path: str) -> Data
        Loads a single dataset, attaches its description and metadata, and returns a `Data` object.

    load() -> None
        Loads all data files in the directory and stores them as a list of `Data` objects in `self.data`.
    """

    def __init__(self, data_loc):
        """
        Initialize the loader with a directory path, discover data files, read the
        optional description JSON, and eagerly load all datasets.

        Parameters
        ----------
        data_loc : str
            Directory containing the tabular files and an optional 'desc.json'.
        """
        data_loc = os.path.abspath(data_loc)
        fileNames = os.listdir(data_loc)
        self.__data_paths = [os.path.join(data_loc, i) for i in fileNames if not i.endswith('.json')]
        self.__data_desc_path = os.path.join(data_loc, 'desc.json')
        self.__data_description_json_format = _data_description_json_format
        self.__load_description()
        self.load()

    def __csv_or_excel(self, path:str) -> str:
        """
        Identify the file type from its extension.

        Parameters
        ----------
        path : str
            Full path to the data file.

        Returns
        -------
        str
            File extension string (e.g., 'csv' or 'xlsx'/'xls'). The method
            returns only the substring after the last dot.
        """
        ext = path.split('.')[-1]
        return ext

    @property
    def data_description_json_template(self) -> None:
        """
        Print the internal JSON template used for the description file.

        Returns
        -------
        None
            This getter prints the template to stdout instead of returning it.
        """
        print(self.__data_description_json_format)

    @data_description_json_template.setter
    def data_description_json_template(self, value:str) -> None:
        """
        Set the internal JSON template used to generate 'desc.json'.

        Parameters
        ----------
        value : str
            A JSON-like string representing the description template schema.

        Returns
        -------
        None
        """
        self.__data_description_json_format = value

    def create_decription_template_file(self, forced:bool=False) -> None:
        """
        Create a 'desc.json' file from the current template if it doesn't exist,
        or overwrite it when `forced=True`.

        Parameters
        ----------
        forced : bool, optional
            If True, overwrite an existing description file. Defaults to False.

        Raises
        ------
        ValueError
            If the description file exists and `forced` is not True.

        Returns
        -------
        None
        """
        if not os.path.exists(self.__data_desc_path) or forced:
            desc = ast.literal_eval(self.data_description_json_template)
            with open(self.__data_desc_path, "w") as json_file:
                json.dump(desc, json_file, indent=4)
            print('Description template file generated.')
        else:
            raise ValueError('Use arguement forced=True if description file exists.')

    def __load_description(self) -> None:
        """
        Load and parse the optional 'desc.json' description file into memory.

        Notes
        -----
        - If the file is missing or invalid, `self.__description` is set to None
          and a message is printed.

        Returns
        -------
        None
        """
        try:
            with open(self.__data_desc_path, 'r') as f:
                desc = json.load(f)
        except Exception as e:
            desc = None
            print('Description file N/A')
        self.__description = desc

    def __loader(self, path:str) -> pd.DataFrame:
        """
        Select the appropriate pandas reader function for the given file path.

        Parameters
        ----------
        path : str
            Full path to the data file.

        Returns
        -------
        Callable
            A callable such as `pd.read_csv` or `pd.read_excel` based on the
            file extension; returns None if the extension is not recognized.
        """
        func = {
            'csv': pd.read_csv,
            'excel': pd.read_excel
        }
        return func.get(self.__csv_or_excel(path))

    @staticmethod
    def __file_name(path:str) -> str:
        """
        Extract the base file name (without the extension) from a file path.

        Parameters
        ----------
        path : str
            Full path to the data file.

        Returns
        -------
        str
            The base name of the file without its extension.
        """
        return os.path.basename(path).split('.')[0]

    def load_data(self, path:str) -> Data:
        """
        Load a single dataset and assemble a corresponding `Data` object.

        This method reads the file into a pandas DataFrame, enriches it with any
        available description and column details from `desc.json`, computes metadata,
        and returns a `Data` wrapper.

        Parameters
        ----------
        path : str
            Full path to the data file.

        Returns
        -------
        Data
            A `Data` object containing the DataFrame and its contextual information.
        """
        data = self.__loader(path)(path)
        data_desc = None
        column_desc = None
        file_name = self.__file_name(path)
        desc = self.__description
        if desc:
            file_desc = desc.get(file_name)
            data_desc = str(file_desc.get('data_desc'))
            column_desc = str(file_desc.get('columns_desc'))
        obj = Data(
            data = data,
            name = file_name,
            data_desc = data_desc,
            column_desc = column_desc,
            metadata = get_metadata(data)
        )
        return obj

    def load(self) -> None:
        """
        Eagerly load all recognized data files and store them as `Data` objects.

        Returns
        -------
        None
        """
        self.data = [self.load_data(i) for i in self.__data_paths]
        