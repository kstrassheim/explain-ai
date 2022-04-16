from numpy import array, any as npany
from pathlib import Path
from ..ml_file_loader import load_ml_model_from_file

class AbstractMLTestingPretrained():
 
    def __init__(self, *args, **kwargs):
        super(AbstractMLTestingPretrained, self).__init__(*args, **kwargs)
        self.trainingClass = None
        self.unit_test_data_filter_scale = 0.01
        self.verbose = False

    def custom_init(self, trainingClass, unit_test_data_filter_scale=0.01):
        self.trainingClass = trainingClass
        self.unit_test_data_filter_scale = unit_test_data_filter_scale

    def unit_test_data_filter(self, data:array): 
        return data[:int(len(data)*self.unit_test_data_filter_scale)]

    def unit_test_testing_data_filter(self, data:array): 
        #from = int(len(data)*self.unit_test_data_filter_scale)+1
        to = int(len(data)*self.unit_test_data_filter_scale)+1+int(len(data)*self.unit_test_data_filter_scale/5)
        return data[:to]

    def test_load_model_run(self):
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        trained_model_file = f'models/{self.trainingClass.__name__}.pkl'
        self.assertTrue(Path(trained_model_file).is_file(), f"Trained model file '{trained_model_file}' does not exist")

        model = load_ml_model_from_file(trained_model_file)
        model.verbose=False
        self.assertIsNotNone(model, "Saved trained model load is None")
        self.assertIsNotNone(model.ml_hash, "ML Hash of saved trained model is None")
        
        self.assertIsNotNone(model.metric, "Result of training should not be None")
        self.assertGreater(model.metric, 0.0, "Result of training must be greater than 0.0")

        training = self.trainingClass(verbose=False, epochs=1)
        X_pred, y_true = training.get_train_data(self.unit_test_testing_data_filter)

        #test preprocessing
        X_prepare = array(model.preprocess(X_pred)).flatten()
        self.assertIsNotNone(X_prepare, "Preprocessing result is None")
        self.assertTrue(len(X_prepare)>0, "Preprocessing result array is empty")
        self.assertTrue(any(((lambda xp : len(xp)>0) for xp in X_prepare)), "Preprocessing results are all ampty")
        #test vectorize
 
        X_trans = array(model.transform(X_prepare)).flatten()
        self.assertIsNotNone(X_trans, "Transformation result is None")
        self.assertTrue(len(X_trans)>0, "Transformation result array is empty")
        self.assertTrue(any(((lambda xp : len(xp)>0) for xp in X_prepare)), "Transformation results are all ampty")

        #test predict
        y_pred = model.predict(X_pred, transform_to_labels=True)
        self.assertIsNotNone(y_pred, "Predicted Result is None")
        self.assertTrue(any(y_pred != 0.0), "Predicted Result do not vary, all predicted labels are 0")
        self.assertTrue(any(y_pred != 1.0), "Predicted Result do not vary, all predicted labels are 1")


