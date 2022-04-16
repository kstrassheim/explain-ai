import unittest
from train_lstm_classifier import LstmClassifierTraining
from classes.abstract import AbstractMLTesting, process_keras_default_unit_test_main_call

class TestLstmClassifierTraining(AbstractMLTesting, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLstmClassifierTraining, self).__init__(True, *args, **kwargs)

        # Custom Code comes here
        self.custom_init(trainingClass=LstmClassifierTraining, unit_test_data_filter_scale=0.001)

if __name__ == '__main__':
    process_keras_default_unit_test_main_call()
    unittest.main()