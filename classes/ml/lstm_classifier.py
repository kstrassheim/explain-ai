from typing import List, Tuple

from numpy import array, ndarray
from sklearn.metrics import classification_report
from ..abstract import AbstractKerasML

class LstmClassifier(AbstractKerasML):
    
    def __init__(self, max_words:int, max_input_len:int, predict_classes_num:int, optimizer_learning_rate:float=1e-4, train_test_metric_field="accuracy", *args, **kwargs):
        self.max_words = max_words
        self.max_input_len = max_input_len
        self._predict_classes_num = predict_classes_num
        super(LstmClassifier, self).__init__(*args, **kwargs)
        self._optimizer_learning_rate = optimizer_learning_rate
        self._train_test_metric_field = train_test_metric_field

    def _get_new_keras_model(self):
        from tensorflow.python.keras.engine.sequential import Sequential
        from tensorflow.keras.layers import Dense, LSTM, Embedding, Activation, Dropout
        return Sequential(layers=[
            Embedding(self.max_words,50,input_length=self.max_input_len),
            LSTM(64),
            Dense(256,name='FC1'),
            Activation('relu'),
            Dropout(0.5),
            Dense(self._predict_classes_num, activation='softmax')])

    def _compile_model(self, model):
        from tensorflow.keras.optimizers import Adam
        model.compile(loss='sparse_categorical_crossentropy', optimizer=Adam(learning_rate=self._optimizer_learning_rate),metrics=[self._train_test_metric_field])     

    def _transform_raw_prediction_to_labels(self, prediction:ndarray)->ndarray:
        from numpy import argmax as npargmax
        return npargmax(prediction, axis=1).flatten()
    
    def _model_apply_test(self, y_true:array, y_pred:array)->Tuple[str, float]:
        resStr = classification_report(y_true, y_pred, zero_division=('warn' if self.verbose else 0))
        resMetric = float(classification_report(y_true, y_pred, output_dict=True, zero_division=('warn' if self.verbose else 0))[self._train_test_metric_field])
        return resStr, resMetric
        


        
