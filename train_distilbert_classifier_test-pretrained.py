import unittest
from train_distilbert_classifier import DistilbertClassifierTraining
from classes.abstract import AbstractMLTestingPretrained, process_keras_default_unit_test_main_call

class TestDistilbertClassifierTraining(AbstractMLTestingPretrained, unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDistilbertClassifierTraining, self).__init__(*args, **kwargs)

        # Custom Code comes here
        self.custom_init(trainingClass=DistilbertClassifierTraining, unit_test_data_filter_scale=0.002)

if __name__ == '__main__':
    process_keras_default_unit_test_main_call()
    unittest.main()