from ..interfaces import ITransformation
from typing import List, Tuple
import numpy as np
import pandas as pd
from numpy import ndarray
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.utils.validation import check_is_fitted, NotFittedError
from ..custom_logging import Logger

class TfIdfTransformation(ITransformation):
    def __init__(self, apply_min_max_scale:bool, max_features:int=None):
        self._mix_max_scaler = (MinMaxScaler() if apply_min_max_scale else None)
        self._max_features = max_features
        self._vectorizer = TfidfVectorizer(max_features=self._max_features) if self._max_features is not None else TfidfVectorizer() 
    def get_name(self)->str: return super().get_name() + (' - MinMaxScaling' if self._mix_max_scaler is not None else '')
    def get_feature_names(self) -> List[str]: return self._vectorizer.get_feature_names()
    def transform(self, docs:List[str]) -> ndarray:
        X = self._vectorizer.transform(docs).toarray()
        if (self._mix_max_scaler is not None):  X = self._mix_max_scaler.transform(X)
        return X
    def fit_transform(self, docs:List[str]) -> ndarray:
        X = self._vectorizer.fit_transform(docs).toarray()
        if (self._mix_max_scaler is not None): X = self._mix_max_scaler.fit_transform(X)
        return X
        
    # Converts vector array into a readable format (rowid, (tfidfvalue, columnname, columnid)) sorted by tfidfvalue descending for every row 
    def convert_vecs_to_readable_format(self, vecs:ndarray, descendingSort:bool=True) -> List[Tuple[int,Tuple[float, str, int]]]:
        featureNames = self.get_feature_names()
        vecframe = pd.DataFrame(vecs, columns=featureNames)
        colview = vecframe.apply(lambda x: x > 0.0).apply(lambda x: list((x.name, sorted([(vecs[x.name,vecframe.columns.get_loc(c)], c, vecframe.columns.get_loc(c))  for c in vecframe.columns[x.values]], reverse=True,key=lambda l: l[0]))), axis=1).tolist() 
        return colview
    def is_fitted(self)->bool:
        try:
            check_is_fitted(self._vectorizer, msg='The tfidf vector is not fitted')
            return True
        except NotFittedError:
            return False