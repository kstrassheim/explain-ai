import uuid
import numpy.testing as npt
from os import remove as osremove
from numpy import array, any as npany
from pathlib import Path
from ..ml_file_loader import load_ml_model_from_file

class AbstractMLTesting():
 
    def __init__(self, test_determinism=True, *args, **kwargs):
        super(AbstractMLTesting, self).__init__(*args, **kwargs)
        self.trainingClass = None
        self.unit_test_data_filter_scale = 0.01
        self.verbose = False
        self.test_determinism = test_determinism

    def custom_init(self, trainingClass, unit_test_data_filter_scale=0.01):
        self.trainingClass = trainingClass
        self.unit_test_data_filter_scale = unit_test_data_filter_scale

    def unit_test_data_filter(self, data:array): 
        return data[:int(len(data)*self.unit_test_data_filter_scale)]

    def unit_test_testing_data_filter(self, data:array): 
        #from = int(len(data)*self.unit_test_data_filter_scale)+1
        to = int(len(data)*self.unit_test_data_filter_scale)+1+int(len(data)*self.unit_test_data_filter_scale/5)
        return data[:to]

    def test_train_save_load_model_run(self):
        training = self.trainingClass(verbose=False, epochs=1)
        model_out_file = f'{uuid.uuid1()}_UNIT_TEST_MODEL.tmp'
        model = training.train(model_out_file, self.unit_test_data_filter)
        
        self.assertIsNotNone(model.metric, "Result of training should not be None")
        self.assertGreater(model.metric, 0.0, "Result of training must be greater than 0.0")
        self.assertTrue(Path(model_out_file).is_file(), "Model file was not saved")
        
        X_pred, y_true = training.get_train_data(self.unit_test_testing_data_filter)

        #test preprocessing
        X_prepare = array(model.preprocess(X_pred)).flatten()
        self.assertIsNotNone(X_prepare, "Preprocessing result is None")
        self.assertTrue(len(X_prepare)>0, "Preprocessing result array is empty")
        self.assertTrue(any(((lambda xp : len(xp)>0) for xp in X_prepare)), "Preprocessing results are all ampty")
        #test vectorize
 
        X_trans = array(model.transform(X_prepare)).flatten()
        self.assertIsNotNone(X_trans, "Transformation result is None")
        self.assertTrue(any(X_trans!=0.0), "Transformation values do not vary, all values are 0")

        #test predict
        y_pred = model.predict(X_pred, transform_to_labels=True)
        self.assertIsNotNone(y_pred, "Predicted Result is None")
        self.assertTrue(any(y_pred != 0.0), "Predicted Result do not vary, all predicted labels are 0")
        self.assertTrue(any(y_pred != 1.0), "Predicted Result do not vary, all predicted labels are 1")

        #test determinism with second model
        if (self.test_determinism):
            model2 = training.train(model_out_file, self.unit_test_data_filter)
            self.assertEqual(model.metric, model2.metric, "The model is not deterministic, second model with same settings results in different metric")
            X_prepare_2 = array(model.preprocess(X_pred)).flatten()
            npt.assert_array_equal(X_prepare, X_prepare_2, "Preprocessing is not deterministic model1 results vary from model2")
            X_trans_2 = array(model.transform(X_prepare_2)).flatten()
            npt.assert_array_equal(X_trans, X_trans_2, "Transformation is not deterministic model1 results vary from model2")
            y_pred_2 = model2.predict(X_pred, transform_to_labels=True)
            npt.assert_array_equal(y_pred, y_pred_2, "Predicted results are not deterministic model1 results vary from model2")

        #test loaded model
        loaded_model = load_ml_model_from_file(model_out_file)
        self.assertIsNotNone(loaded_model, "Model could not be loaded")
        self.assertEqual(model.metric, loaded_model.metric, "The loaded models metric is different from the first")
        X_prepare_loaded = array(loaded_model.preprocess(X_pred)).flatten()
        npt.assert_array_equal(X_prepare, X_prepare_loaded, "Preprocessing results in generated and loaded model are not the same")
        X_trans_loaded = array(loaded_model.transform(X_prepare_loaded)).flatten()
        npt.assert_array_equal(X_trans, X_trans_loaded, "Transformation results in generated and loaded model are not the same")
        y_pred_loaded = loaded_model.predict(X_pred, transform_to_labels=True)
        npt.assert_array_equal(y_pred, y_pred_loaded, "Predicted results from generated and loaded model are not the same")

        #delete generated model file after testing
        osremove(model_out_file)
        self.assertFalse(Path(model_out_file).is_file(), "Saved model file was not deleted properly")

    def test_saved_trained_model_is_same_as_code(self):
        trained_model_file = f'models/{self.trainingClass.__name__}.pkl'
        self.assertTrue(Path(trained_model_file).is_file(), f"Trained model file '{trained_model_file}' does not exist")

        loaded_trained_model = load_ml_model_from_file(trained_model_file)
        self.assertIsNotNone(loaded_trained_model, "Saved trained model load is None")
        self.assertIsNotNone(loaded_trained_model.ml_hash, "ML Hash of saved trained model is None")
        
        training = self.trainingClass(force_cpu = loaded_trained_model.force_cpu, verbose=loaded_trained_model.verbose, epochs=loaded_trained_model.get_epochs())
        new_ml_hash = training.get_current_ml_hash_code()
        self.assertEqual(loaded_trained_model.ml_hash, new_ml_hash, f"ML Hash code of saved trained model '{trained_model_file}' and new trained model differ, try retrain model - saved_model_hash_code:{loaded_trained_model.ml_hash} != new_model_hash_code:{new_ml_hash}")

        # change hash code by data
        changed_data_ml_hash = training.get_current_ml_hash_code(self.unit_test_data_filter)
        self.assertNotEqual(changed_data_ml_hash, new_ml_hash, f"ML Hash code should differ by changing training data - changed_data_ml_hash:{changed_data_ml_hash} == last_model_hash_code:{new_ml_hash}")       
        
        # change hash code by settings
        training.force_cpu = not training.force_cpu
        changed_settings_ml_hash = training.get_current_ml_hash_code(self.unit_test_data_filter)
        self.assertNotEqual(changed_data_ml_hash, changed_settings_ml_hash, f"ML Hash code should differ by changing settings - changed_data_ml_hash:{changed_data_ml_hash} == changed_settings_ml_hash:{changed_settings_ml_hash}")       

        # train again to get the same hash code
        training2 = self.trainingClass(force_cpu = loaded_trained_model.force_cpu, verbose=loaded_trained_model.verbose, epochs=loaded_trained_model.get_epochs())
        new_ml_hash2 = training2.get_current_ml_hash_code()
        self.assertEqual(new_ml_hash, new_ml_hash2 , f"ML Hash code generation not deterministic model1 and model2 differ, model1_hash_code:{new_ml_hash} != model2_hash_code:{new_ml_hash2}")
