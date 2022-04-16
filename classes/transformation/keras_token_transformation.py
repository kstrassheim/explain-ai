from ..interfaces import ITransformation
from typing import List, Tuple
import numpy as np
import pandas as pd
from numpy import ndarray

from ..custom_logging import Logger

class KerasSequenceTransformation(ITransformation):
    def __init__(self, max_output_len:int):
        self.max_output_len = max_output_len
    def get_name(self)->str: return super().get_name()
    def get_feature_names(self) -> List[str]: return []
    def transform(self, docs:List[str]) -> ndarray:
        from tensorflow.keras.preprocessing import sequence
        return sequence.pad_sequences(docs,maxlen=self.max_output_len)
    def fit_transform(self, docs:List[str]) -> ndarray:
        return self.transform(docs)
        
    # Converts vector array into a readable format (rowid, (tfidfvalue, columnname, columnid)) sorted by tfidfvalue descending for every row 
    def convert_vecs_to_readable_format(self, vecs:ndarray, descendingSort:bool=True) -> List[Tuple[int,Tuple[float, str, int]]]:
        pass
    def is_fitted(self)->bool:
        return True