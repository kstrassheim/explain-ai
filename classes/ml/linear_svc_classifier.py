from typing import List, Tuple

from numpy import array, ndarray
from sklearn import svm
from sklearn.metrics import classification_report
from ..abstract import AbstractML
from numpy import argmax as npargmax

class LinearSvcClassifier(AbstractML):
    
    def __init__(self, tolerance=1e-4, train_test_metric_field="accuracy", *args, **kwargs):
        self._train_test_metric_field = train_test_metric_field
        self._tolerance=tolerance
        super(LinearSvcClassifier, self).__init__(*args, **kwargs)
        self.svc = svm.SVC(random_state=self._random_seed, tol=self._tolerance)

    def _transform_raw_prediction_to_labels(self, prediction:ndarray)->ndarray:
        return npargmax(prediction, axis=1).flatten()
    
    def _model_apply_test(self, y_true:array, y_pred:array)->Tuple[str, float]:
        resStr = classification_report(y_true, y_pred, zero_division=('warn' if self.verbose else 0))
        resMetric = float(classification_report(y_true, y_pred, output_dict=True, zero_division=('warn' if self.verbose else 0))[self._train_test_metric_field])
        return resStr, resMetric
    
   
    def _model_predict(self, X_vec:ndarray) -> ndarray: 
        pred = self.svc.predict(X_vec)
        return array([[0 if p == 1 else 1, 1 if p == 1 else 0] for p in pred])

    # Training the model -> Returns raw test prediction
    def _model_train(self, X_train, y_train:array, X_val, y_val:array):
       self.svc.fit(X_train, y_train)

    def _model_predict_raw_test_data(self, X_test:ndarray)->ndarray: 
        return self._model_predict(X_test)
