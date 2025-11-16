from dataclasses import dataclass
import pandas as pd
from zenalyze.data.data_base_class import Data, DataLoad
from zenalyze.data.pandas.metadata import get_metadata


@dataclass
class PandasData(Data):
    @property
    def get_class_name(self):
        return self.__class__.__name__


class PandasDataLoad(DataLoad):

    def __init__(self, data_loc):
        super().__init__(data_loc, get_metadata)

    @property
    def get_class_name(self):
        return self.__class__.__name__

    def _loader(self, path:str) -> pd.DataFrame:
        func = {
            'csv': pd.read_csv,
            'excel': pd.read_excel
        }
        return func.get(self._file_extn(path))


