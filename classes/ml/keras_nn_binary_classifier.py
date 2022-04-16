from typing import List, Tuple
from numpy import array, ndarray
from ..abstract import AbstractKerasML

class KerasNNBinaryClassifier(AbstractKerasML):
    
    def __init__(self, optimizer_learning_rate:float=1e-4, train_test_metric_field="accuracy", *args, **kwargs):
        super(KerasNNBinaryClassifier, self).__init__(*args, **kwargs)
        self._optimizer_learning_rate = optimizer_learning_rate
        self._train_test_metric_field = train_test_metric_field

    def _get_new_keras_model(self):
        from tensorflow.python.keras.engine.sequential import Sequential
        from tensorflow.keras.layers import Dense
        return Sequential(layers=[
            Dense(2096, activation='relu'),
            Dense(1048, activation='relu'),
            Dense(512, activation='relu'),
            Dense(256, activation='relu'),
            Dense(128, activation='relu'),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')])

    def _compile_model(self, model):
        from tensorflow.keras.optimizers import Adam
        model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=self._optimizer_learning_rate),metrics=[self._train_test_metric_field])     

    def _transform_raw_prediction_to_labels(self, prediction:ndarray)->ndarray:
        from numpy import round as npround
        return npround(prediction).flatten()
    
    def _model_apply_test(self, y_true:array, y_pred:array)->Tuple[str, float]:
        from sklearn.metrics import classification_report
        resStr = classification_report(y_true, y_pred, zero_division=('warn' if self.verbose else 0))
        resMetric = float(classification_report(y_true, y_pred, output_dict=True, zero_division=('warn' if self.verbose else 0))[self._train_test_metric_field])
        return resStr, resMetric
        


        
