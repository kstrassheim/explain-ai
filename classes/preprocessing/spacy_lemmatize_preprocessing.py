from os import XATTR_CREATE
from ..interfaces import IPreprocessing
from numpy import array as nparray, ndarray, generic
from pickle import load as pklload

class SpacyLemmatizePreprocessing(IPreprocessing):
    def __init__(self, spacy_model_name = "en_core_web_sm", max_text_length=None):
        self._spacy_model_name = spacy_model_name
        self.__max_text_length = max_text_length

    def get_name(self)->str: return super().get_name() + " - " + self._spacy_model_name

    def __load_nlp(self):
        model = None
        with open(f"nlp/{self._spacy_model_name}.pkl",'rb') as infile:
            model = pklload(infile)
        return model

    def _preprocess_text(self, doc):
        d = doc[0:self.__max_text_length] if self.__max_text_length is not None and self.__max_text_length > 0 else doc
        #Lemmatize and remove stop words
        return " ".join([t.lemma_.lower() for t in d if not t.is_stop])

    def fit_transform(self, data):
        return self.transform(data)

    def transform(self, data:nparray):
        nlp = self.__load_nlp()
        # handle if argument is given as normal list and not numpy
        if isinstance(data,(ndarray,generic)):
            data = data.tolist()
        docs = nlp.pipe(data, n_process=(1), disable=["tok2vec", "parser"]) 
        return nparray([self._preprocess_text(d) for d in docs])

    def is_fitted(self)->bool:
        return True