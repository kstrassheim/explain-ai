import types
import pandas as pd
import numpy as np
from classes.abstract import AbstractMLTraining
from classes.ml import KerasNNSoftmaxClassifier
from classes.transformation import TfIdfTransformation
from classes.preprocessing import SpacyLemmatizePreprocessing, IdentityPreprocessing

class LemmaTfIdfNNClassifierTraining(AbstractMLTraining):

    def __init__(self, force_cpu = True, verbose=True, epochs=1):
        super(LemmaTfIdfNNClassifierTraining, self).__init__(force_cpu=force_cpu,verbose=verbose,epochs=epochs)
        self.DATASET_PATH:str = 'datasets/data.csv'
        self.DATASET_INDEX_COLUMN:str = 'id'
        self.DATASET_LEARNING_COLUMN:str = 'text'
        self.DATASET_LABEL_COLUMN:str = 'label'
    def get_new_classifier_instance(self):
        return KerasNNSoftmaxClassifier(
                    predict_classes_num = 2,
                    preprocessing = SpacyLemmatizePreprocessing(),
                    transformation = TfIdfTransformation(apply_min_max_scale=False, max_features=20000),
                    random_seed = 1337, 
                    test_split_ratio = 0.2,
                    batch_size = 32,
                    epochs = self.epochs,
                    optimizer_learning_rate=0.0001,

                    # settings not mandatory for ml hash
                    force_cpu = self.force_cpu,
                    verbose=self.verbose
                    )

    def get_train_data(self, data_filter_func:types.FunctionType=None)->np.array:
        data = pd.read_csv(self.DATASET_PATH, index_col=self.DATASET_INDEX_COLUMN)
        # Apply external filter if available
        if data_filter_func is not None: data = data_filter_func(data)
        # Retreive training data
        X=data[self.DATASET_LEARNING_COLUMN].replace(np.nan, '', regex=False).to_numpy()
        # X = np.array([d if d is not np.nan else '' for d in data[self.DATASET_LEARNING_COLUMN]])
        y = data[self.DATASET_LABEL_COLUMN].to_numpy()
        return X, y

    # MAIN Programm
    def train(self, save_trained_model_path:str, data_filter_func:types.FunctionType=None):
        # DO Custom stuff here
        return super().train(save_trained_model_path, data_filter_func)

# execute only if not run by external file
if __name__ == "__main__":
    # LOAD Environment Variables
    from os import getenv, environ
    from dotenv import load_dotenv
    
    # GET Environment Variables
    load_dotenv()
    FORCE_CPU:bool = getenv('FORCE_CPU', 'False').lower() == 'true'
    VERBOSE:bool = getenv('VERBOSE', 'True').lower() == 'true'

    # Set TF Log Level
    environ['TF_CPP_MIN_LOG_LEVEL'] = f"{int(getenv('TF_LOG_LEVEL', '3'))}"  

    training = LemmaTfIdfNNClassifierTraining(force_cpu=True, verbose=VERBOSE, epochs=1) 
    # train new model and save it to models path
    model = training.train(f'models/{type(training).__name__}.pkl', None)