from typing import List, Tuple

from numpy import array, ndarray
from sklearn.metrics import classification_report
from ..abstract import AbstractML

class HuggingFacePretrainedClassifier(AbstractML):
    
    def __init__(self, pretrained_model_path:str, max_input_len:int, predict_classes_num:int, optimizer_learning_rate:float=1e-4, train_test_metric_field="accuracy", *args, **kwargs):

        super(HuggingFacePretrainedClassifier, self).__init__(*args, **kwargs)
        self._pretrained_model_path = pretrained_model_path
        self._max_input_len = max_input_len
        self._predict_classes_num = predict_classes_num
        self._optimizer_learning_rate = optimizer_learning_rate
        self._train_test_metric_field = train_test_metric_field
        self._tf_model_weights = None
        self._tokenizer = None

        self.__predict_model_cached  = None

    def get_name(self):
        return f'{super().get_name()} - {self._pretrained_model_path}'

    def clear_cache(self):
         self.__predict_model_cached = None
         
    def get_ml_hash(self, X:ndarray, y:array)->str:
        self.__predict_model_cached  = None
        # !!! Absolute mandatory to clear tf session after training or tests will result in other hash code
        from tensorflow.keras.backend import clear_session
        clear_session()
        return super().get_ml_hash(X,y)

    def __get_model(self):
        timestamp_load_model = self._logger.get_timestamp()

        import tensorflow as tf
        # DISABLE Messages
        import logging
        tf.get_logger().setLevel(logging.ERROR)
        from transformers import TFAutoModelForSequenceClassification, logging as hf_logging    
        hf_logging.set_verbosity_error()
        from tensorflow.python.util import deprecation
        deprecation._PRINT_DEPRECATION_WARNINGS = False
        # END DISABLE Messages
        model = TFAutoModelForSequenceClassification.from_pretrained(self._pretrained_model_path, num_labels=self._predict_classes_num)

        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.losses import SparseCategoricalCrossentropy
        model.compile(loss=SparseCategoricalCrossentropy(from_logits=True), optimizer=Adam(learning_rate=self._optimizer_learning_rate),metrics=[self._train_test_metric_field])   

        if self.verbose: self._logger.log_duration("Load Model Duration", timestamp_load_model)

        timestamp_set_weights_to_model = self._logger.get_timestamp()
        # LOAD learned Weights into model
        if (self._tf_model_weights is not None): 
            model.set_weights(self._tf_model_weights)
            if self.verbose: self._logger.log_duration("Set Weights to Model Duration", timestamp_set_weights_to_model)

        return model

    def __get_tokenizer(self):
        if self._tokenizer is None:
            from transformers import AutoTokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(self._pretrained_model_path)
        return self._tokenizer


    def _transform_raw_prediction_to_labels(self, prediction:ndarray)->ndarray:
        from numpy import argmax as npargmax
        return npargmax(prediction, axis=1).flatten()
    
    def _model_apply_test(self, y_true:array, y_pred:array)->Tuple[str, float]:
        resStr = classification_report(y_true, y_pred, zero_division=('warn' if self.verbose else 0))
        resMetric = float(classification_report(y_true, y_pred, output_dict=True, zero_division=('warn' if self.verbose else 0))[self._train_test_metric_field])
        return resStr, resMetric
    
   
    def _model_predict(self, X_vec:ndarray) -> ndarray: 
        
        tokenizer = self.__get_tokenizer();
        X_vec_input = array([X_vec]).tolist() if type(X_vec) == str else array(X_vec).tolist()
        X_vec_trans = tokenizer(X_vec_input, return_tensors='tf', truncation=True, padding=True, max_length=self._max_input_len, verbose=False)

        self.__predict_model_cached  = self.__predict_model_cached if self.__predict_model_cached is not None else self.__get_model()
        if self.force_cpu:
            from tensorflow import device as tfdevice
            with tfdevice('/gpu:0' if self.force_cpu else '/cpu:0'):
                self._logger.log_warning("Tensorflow - Using CPU - GPU deactivated by settings")
                return self.__predict_model_cached.predict(X_vec_trans.data).logits
        else: 
            return self.__predict_model_cached.predict(X_vec_trans.data).logits

    # Training the model -> Returns raw test prediction
    def _model_train(self, X_train, y_train:array, X_val, y_val:array):
        tokenizer = self.__get_tokenizer();
        X_train_trans = tokenizer(X_train.tolist(), return_tensors='tf', truncation=True, padding=True, max_length=self._max_input_len, verbose=False)
        X_val_trans = tokenizer(X_val.tolist(), return_tensors='tf', truncation=True, padding=True, max_length=self._max_input_len, verbose=False)
        model = self.__get_model()
        if self.force_cpu:
            from tensorflow import device as tfdevice
            with tfdevice('/cpu:0'):
                self._logger.log_warning("Tensorflow - Using CPU - GPU deactivated by settings")
                model.fit(X_train_trans.data, y_train, batch_size=self._batch_size, epochs=self._epochs,
                    validation_data=(X_val_trans.data, y_val),
                    verbose=(1 if self.verbose else 0))
        else:
            model.fit(X_train_trans.data, y_train, batch_size=self._batch_size, epochs=self._epochs,
                    validation_data=(X_val_trans.data, y_val),
                    verbose=(1 if self.verbose else 0))

        self._tf_model_weights = model.get_weights()

    def _model_predict_raw_test_data(self, X_test:ndarray)->ndarray: return self._model_predict(X_test)
        


        
