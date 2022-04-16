from typing import Tuple
from numpy import ndarray, array
from ..custom_logging import Logger
from hashlib import sha1 
from pickle import dumps
from sklearn.model_selection import train_test_split
from ..interfaces import IML, ITransformation, IPreprocessing
from ..preprocessing import IdentityPreprocessing

class AbstractML(IML):
    def __init__(self, 
        transformation:ITransformation,
        preprocessing:IPreprocessing = IdentityPreprocessing(),
        random_seed:int = 0,
        test_split_ratio=0.2, 
        batch_size:int=32, 
        epochs:int=1,

        force_cpu:bool = True,
        verbose:bool=False):
        
        if self.__class__ == AbstractML:
            raise Exception('Not possible to call abstract class init directly')

        self._transformation = transformation
        self._preprocessing = preprocessing
        self._random_seed:int = random_seed
        
        self._test_split_ratio:int = test_split_ratio
        self._batch_size:int = batch_size
        self._epochs:int = epochs

        self.force_cpu:bool = force_cpu
    
        self._logger = Logger(verbose=verbose)
        self.verbose = verbose

        # reset result
        self.metric:float = None
        self.ml_hash = None
    def get_name(self):
        return type(self).__name__
    def get_epochs(self):
        return self._epochs
    def get_verbose(self):
        return self.__verbose
    def set_verbose(self, verbose:bool):
        self.__verbose = verbose
        if self._logger is not None : self._logger.verbose = verbose

    def preprocess(self, X):
        fitted = self._preprocessing.is_fitted()
        if (not fitted): assert False, "Preprocessing is not fitted, apply fit first"
        return self._preprocessing.transform(X) 

    def transform(self, X):
        fitted = self._transformation.is_fitted()
        if (not fitted): assert False, "Transformation is not fitted, apply fit first"
        return self._transformation.transform(X)
    def clear_cache(self):
        pass
    def get_ml_hash(self, X:ndarray, y:array)->str:
        # save log variables
        # tmp_force_cpu = self.force_cpu
        # tmp_verbose = self.verbose
        # tmp_tf_training_log_level = self.tf_training_log_level
        
        # #deactivate log variables for proper hash generation
        # self.force_cpu = False
        # self.verbose = False
        # self.tf_training_log_level = 0

        self_hash = sha1(dumps(self)).hexdigest()
        ystr = sha1(y).hexdigest()
        xstr = sha1(X[0].encode()).hexdigest()
        h = sha1((self_hash+ystr+xstr+str(len(X))).encode()).hexdigest()

        # reset log variables
        # self.force_cpu = tmp_force_cpu
        # self.verbose = tmp_verbose
        # self.tf_training_log_level = tmp_tf_training_log_level

        return h

    def __reset_ml_hash(self, X:ndarray, y:array):
        # Reset ML Hash !! Important 
        self.ml_hash = None
        self.ml_hash = self.get_ml_hash(X, y)

    def _model_predict(self, X_vec:ndarray) -> ndarray:
        assert False, "This method should be overriden by parent class"
        X_trans = self.transform(X)

    def _transform_raw_prediction_to_labels(self, prediction:ndarray)->ndarray:
        assert False, "This method should be overriden by parent class"

    def predict(self, X:ndarray, transform_to_labels:bool=False) -> ndarray:
        X = array([X]) if type(X)== str else array(X)
        X_prep = self.preprocess(X)
        X_trans = self.transform(X_prep)
        raw_prediction = self._model_predict(X_trans)
        if not transform_to_labels: return raw_prediction
        else:
            y_pred = self._transform_raw_prediction_to_labels(raw_prediction)
            return y_pred

     # Training the model -> Returns trained accuracy as result
    def _model_train(self, X_train, y_train:array, X_val, y_val:array):
         assert False, "This method should be overriden by parent class"

    def _model_predict_raw_test_data(self, X_test:ndarray)->ndarray:
        assert False, "This method should be overriden by parent class"

    def _model_apply_test(self, y_true:array, y_pred:array)->Tuple[str, float]:
        assert False, "This method should be overriden by parent class"

    # Training the model -> Returns or any other metric as single value result
    def fit(self, X:ndarray, y:array)->float:
        # important to call before every training
        self.__reset_ml_hash(X, y)
        self._logger.log_info(f"Started training of {self.get_name()} - ml hash: {self.ml_hash}")
   
        # Reset accuracy
        self.accuracy:float = None

        timestamp_preprocessing = self._logger.get_timestamp() 
        self._logger.log_info(f'Started Preprocessing with {self._preprocessing.get_name()}')
        X_prep = self._preprocessing.fit_transform(X)
        self._logger.log_success(f'Preprocessing - {self._preprocessing.get_name()} - completed')
        self._logger.log_duration("Preprocessing Duration", timestamp_preprocessing)

        # Transformation
        timestamp_transform = self._logger.get_timestamp() 
        self._logger.log_info(f'Started Transformation with {self._transformation.get_name()}')
        X_trans = self._transformation.fit_transform(X_prep)
        self._logger.log_success(f'Transformation - {self._transformation.get_name()} - completed')
        self._logger.log_duration("Transformation Duration", timestamp_transform)

        # Split Data into train, validation and test
        assert self._test_split_ratio > 0.0 and self._test_split_ratio < 1.0, "Test split ratio has to be a float number beetween 0 and 1"
        timestamp_split = self._logger.get_timestamp()
        X_trans_ids = list(range(len(X_trans)))
        X_train_ids, X_test_ids, y_train, y_test = train_test_split(X_trans_ids, y, test_size=self._test_split_ratio, random_state=self._random_seed, shuffle=True)
        X_train_ids, X_val_ids, y_train, y_val = train_test_split(X_train_ids, y_train, test_size=self._test_split_ratio * len(X) / len(X_train_ids), random_state=self._random_seed, shuffle=True)
        
        X_train = X_trans[X_train_ids]
        X_test = X_trans[X_test_ids]
        X_val = X_trans[X_val_ids]
        
         # 0.25 x 0.8 = 0.2
        self._logger.log_success(f"Validation split - Len Train X:{len(X_train)}, Len Val X:{len(X_val)}, Len Test X:{len(X_test)}, Len Train y:{len(y_train)}, Len Val y:{len(y_val)}, Len Test y:{len(y_test)}")
        self._logger.log_duration("Validation split Duration", timestamp_split)
        
        # TRAINING
        timestamp_training = self._logger.get_timestamp()
        self._model_train(X_train, y_train, X_val, y_val)
        self._logger.log_success("Training performed")
        self._logger.log_duration("Training Duration", timestamp_training)
       
        # TESTING
        timestamp_testing = self._logger.get_timestamp()
        y_test_pred = self._model_predict_raw_test_data(X_test)
        y_pred = self._transform_raw_prediction_to_labels(y_test_pred)
        y_true = y_test.flatten()
        self._logger.log_success("Testing Result:")
        resultStr, resultMetric =self._model_apply_test(y_true, y_pred)
        self._logger.log_success(resultStr)
        self._logger.log_duration("Testing Duration", timestamp_testing)
        # TESTING
        self.metric = resultMetric
        return self.metric