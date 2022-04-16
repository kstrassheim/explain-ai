from typing import List, Tuple
from numpy import ndarray, array

class IML():
    def fit(self, X:ndarray, y:array)->float:
        pass
    def predict(self, X:ndarray) -> ndarray:
        pass

class IPreprocessing():
    def get_name(self)->str: return type(self).__name__
    def fit_transform(self, X:ndarray)->ndarray:
        pass
    def transform(self, docs:array) -> ndarray:
        pass
    def is_fitted(self)->bool:
        pass

class ITransformation():
    def get_name(self)->str: return type(self).__name__
    def fit_transform(self, docs:array) -> ndarray:
        pass
    def transform(self, docs:array) -> ndarray:
        pass
    def get_feature_names(self) -> List[str]:
        pass
    def convert_vecs_to_readable_format(self, vecs:ndarray, descendingSort:bool=True) -> List[Tuple[int,Tuple[float, str, int]]]:
        pass
    def is_fitted(self)->bool:
        pass

