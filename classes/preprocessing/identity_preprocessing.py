from ..interfaces import IPreprocessing

class IdentityPreprocessing(IPreprocessing):
    def fit_transform(self, data):
        return data
    def transform(self, data):
        return data
    def is_fitted(self)->bool:
        return True