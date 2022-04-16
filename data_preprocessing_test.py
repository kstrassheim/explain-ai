# DISABLE ALL TF LOG !!! HAS TO BE SET AT EVERY POSSIBLE STARTUP FILE AT BEGINNING WHYEVER
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# LOAD Environment Variables
from os import getenv
from dotenv import load_dotenv
load_dotenv()

UNIT_TEST_DATA_FILTER_SCALE:float = float(getenv('UNIT_TEST_DATA_FILTER_SCALE', '0.01'))
UNIT_TEST_VERBOSE:bool = getenv('UNIT_TEST_VERBOSE', 'True').lower() == 'true'

# set up logging
import warnings
if UNIT_TEST_VERBOSE == False: 
    warnings.filterwarnings("ignore")
    warnings.filterwarnings("ignore", category=DeprecationWarning)

# Import
import unittest
from numpy import array
from data_preprocessing import data_preprocessing

def unit_test_data_filter(data:array): 
    return data[:int(len(data)*UNIT_TEST_DATA_FILTER_SCALE)]

class TestDataPreprocessing(unittest.TestCase):
    def test_data_preprocessing_run(self):
        res = data_preprocessing(None, unit_test_data_filter, verbose=UNIT_TEST_VERBOSE)
        self.assertIsNotNone(res, "Result of data_preprocessing should not be None")
        self.assertGreater(res, 0, "Result of data_preprocessing must be greater than 0")

if __name__ == '__main__':
    unittest.main()