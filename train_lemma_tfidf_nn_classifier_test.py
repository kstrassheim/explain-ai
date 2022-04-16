import unittest
from train_lemma_tfidf_nn_classifier import LemmaTfIdfNNClassifierTraining
from classes.abstract import AbstractMLTesting, process_keras_default_unit_test_main_call

class TestLemmaTfIdfNNClassifierTraining(AbstractMLTesting, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestLemmaTfIdfNNClassifierTraining, self).__init__(True, *args, **kwargs)

        # Custom Code comes here
        self.custom_init(trainingClass=LemmaTfIdfNNClassifierTraining, unit_test_data_filter_scale=0.001)

if __name__ == '__main__':
    process_keras_default_unit_test_main_call()
    unittest.main()