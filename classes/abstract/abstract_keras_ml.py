# LOAD Environment Variables
from os import environ
import random
from numpy import random as nprandom, array, ndarray

from .abstract_ml import AbstractML

class AbstractKerasML(AbstractML):
    def __init__(self, *args, **kwargs):

        super(AbstractKerasML, self).__init__(*args, **kwargs)

        # START SET RANDOMNESS

        # Set Tensorflow deterministic setting to SAME Resu:lts on GPU
        environ['TF_DETERMINISTIC_OPS'] = '1'

        environ['PYTHONHASHSEED']=str(self._random_seed)
        random.seed(self._random_seed)
        nprandom.seed(self._random_seed)
        # !!! Important to import tensorflow after setting numpy seeds
        # SET TF Log Level !!! Can be only set once
        import tensorflow as tf

        tf.config.enable_deterministic_ops = True
        tf.random.set_seed(self._random_seed)

        #END SET RANDOMNESS

        # Reset keras model
        self._tf_model_json = self._get_new_keras_model().to_json()
        self._tf_model_input_shape = None
        # Reset weights
        self._tf_model_weights = None

    def clear_cache(self):
         self.__predict_model_cached = None
    def get_ml_hash(self, X:ndarray, y:array)->str:
        # !!! Absolute mandatory to clear tf session after training or tests will result in other hash code
        self.__predict_model_cached = None
        from tensorflow.keras.backend import clear_session
        clear_session()
        return super().get_ml_hash(X,y)

    def _get_new_keras_model(self):
        assert False, "This method should be overriden by parent class"

    def _compile_model(self,model):
        assert False, "This method should be overriden by parent class"

    def __get_model(self):
        timestamp_load_model = self._logger.get_timestamp()
        from tensorflow.keras.models import model_from_json
        assert self._tf_model_json is not None, "Model cannot be get - JSON attribute is NONE - Save new model with save_model Function in your parent class"
        model = model_from_json(self._tf_model_json)
        self._compile_model(model)
        
        # Build model by input shape and load weights if available
        if (self._tf_model_input_shape is not None):
            model.build(self._tf_model_input_shape)
        # LOAD learned Weights into model
        if (self._tf_model_weights is not None): 
            model.set_weights(self._tf_model_weights)
        if self.verbose: self._logger.log_duration("Load Model Duration", timestamp_load_model)
        return model


    def _model_predict(self, X_vec:ndarray) -> ndarray: 
        self.__predict_model_cached  = self.__predict_model_cached if self.__predict_model_cached is not None else self.__get_model()

        if self.force_cpu:
            from tensorflow import device as tfdevice
            with tfdevice('/cpu:0'):
                self._logger.log_warning("Tensorflow - Using CPU - GPU deactivated by settings ")
                return self.__predict_model_cached.predict(X_vec)
        else:
             return self.__predict_model_cached.predict(X_vec)

     # Training the model -> Returns raw test prediction
    def _model_train(self, X_train:ndarray, y_train:array, X_val:ndarray, y_val:array):
        # TRAINING
        model = self.__get_model()
        if self.force_cpu:
            from tensorflow import device as tfdevice
            with tfdevice('/cpu:0'):
                self._logger.log_warning("Tensorflow - Using CPU - GPU deactivated by settings ")
                model.fit(X_train, y_train, batch_size=self._batch_size, epochs=self._epochs,
                        validation_data=(X_val, y_val),
                        verbose=(1 if self.verbose else 0))
        else:
            model.fit(X_train, y_train, batch_size=self._batch_size, epochs=self._epochs,
                        validation_data=(X_val, y_val),
                        verbose=(1 if self.verbose else 0))

        # SAVE weights after training
        self._tf_model_weights = model.get_weights()
        self._tf_model_input_shape = model.input_shape
        

    def _model_predict_raw_test_data(self, X_test:ndarray)->ndarray: return self._model_predict(X_test)
       
        
