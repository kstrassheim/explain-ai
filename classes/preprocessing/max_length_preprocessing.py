from os import XATTR_CREATE
from ..interfaces import IPreprocessing
from numpy import array as nparray, ndarray, generic

class MaxLengthPreprocessing(IPreprocessing):
    def __init__(self, max_text_length=1000):
        self.__max_text_length = max_text_length

    def fit_transform(self, data):
        return self.transform(data)

    def transform(self, data:nparray):
        return nparray([d[0:self.__max_text_length] for d in data])

    def is_fitted(self)->bool:
        return True