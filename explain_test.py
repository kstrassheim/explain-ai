import unittest
from explain import Explain

class TestExplain(unittest.TestCase):
    pass
#     def test_dummy(self):
# #Load Model
#     model = load_ml_model_from_file('models/KerasTfIdfNNSimpleClassifierTraining.pkl')
#     model.verbose = model.verbose = model.logger.verbose=False
    
#     #CHANGE model.predict to predict_lime_bypass IF BYPASS NEEDED
#     l = Lime(predict=model.predict, class_names = ['No Fake News', 'Fake News'])

#         l = Explain()


#         res = l.run()
#         self.assertTrue(res[0]==1.0, "Lime dummy result is not correct")

if __name__ == '__main__':  
    # Disable TF Log Level
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 

    # process_default_unit_test_main_call()
    unittest.main()