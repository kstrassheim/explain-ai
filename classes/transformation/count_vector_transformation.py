from ..interfaces import ITransformation
from typing import List, Tuple
import numpy as np
import pandas as pd
from numpy import ndarray
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.utils.validation import check_is_fitted, NotFittedError
        
class CountVectorTransformation(ITransformation):
    def __init__(self):
        self.vectorizer = CountVectorizer() 
    def get_feature_names(self) -> List[str]:
        return self.vectorizer.get_feature_names()
    def transform(self, docs:List[str]) -> ndarray:
        return self.vectorizer.transform(docs).toarray()
    def fit_transform(self, docs:List[str]) -> ndarray:
        return self.vectorizer.fit_transform(docs).toarray()
    # Converts vector array into a readable format (rowid, (count value, columnname, columnid)) sorted by tfidfvalue descending for every row 
    def convert_vecs_to_readable_format(self, vecs:ndarray, descendingSort:bool=True) -> List[Tuple[int,Tuple[float, str, int]]]:
        featureNames = self.get_feature_names()
        vecframe = pd.DataFrame(vecs, columns=featureNames)
        colview = vecframe.apply(lambda x: x > 0.0).apply(lambda x: list((x.name, sorted([(vecs[x.name,vecframe.columns.get_loc(c)], c, vecframe.columns.get_loc(c))  for c in vecframe.columns[x.values]], reverse=True,key=lambda l: l[0]))), axis=1).tolist() 
        return colview
    def is_fitted(self)->bool:
        try:
            check_is_fitted(self.vectorizer, msg='The count vector is not fitted')
            return True
        except NotFittedError:
            return False