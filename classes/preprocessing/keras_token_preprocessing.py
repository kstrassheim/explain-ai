from ..interfaces import IPreprocessing
import numpy as np

class KerasTokenPreprocessing(IPreprocessing):
    def __init__(self, max_words):
        self.max_words = max_words
        from tensorflow.keras.preprocessing.text import Tokenizer
        self.tokenizer = Tokenizer(num_words=max_words)
        self.__is_fitted = False
    def fit_transform(self, data):
        self.tokenizer.fit_on_texts(data)
        self.__is_fitted = True
        return np.array(self.tokenizer.texts_to_sequences(data), dtype=object)
    def transform(self, data):
        return np.array(self.tokenizer.texts_to_sequences(data), dtype=object)
    def is_fitted(self)->bool:
        return self.__is_fitted