import types
import numpy as np
from .abstract_keras_ml import AbstractKerasML
from ..ml_file_loader import save_ml_model_to_file

class AbstractMLTraining:
    def __init__(self,force_cpu=False, verbose:bool=True, epochs=1):
        self.force_cpu = force_cpu
        self.verbose = verbose
        self.epochs = epochs

    def get_new_classifier_instance(self):
        assert False, "This method should be overriden by parent class"

    def get_train_data(data_filter_func:types.FunctionType=None)->np.array:
        assert False, "This method should be overriden by parent class"

    def get_current_ml_hash_code(self, data_filter_func:types.FunctionType=None)->str:
        X, y = self.get_train_data(data_filter_func)
        model:AbstractKerasML = self.get_new_classifier_instance()
        return model.get_ml_hash(X, y)

    def train(self, save_trained_model_path:str, data_filter_func:types.FunctionType=None)->AbstractKerasML:
        # Load Train Data
        X, y = self.get_train_data(data_filter_func)

        # Apply ML
        model:AbstractKerasML = self.get_new_classifier_instance()

        model.fit(X, y)       

        # Save model to file if successfull
        if (save_trained_model_path is not None):
            save_ml_model_to_file(model, save_trained_model_path)
        #return model as result
        return model