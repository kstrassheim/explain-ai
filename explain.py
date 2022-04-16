from classes.ml_file_loader import load_ml_model_from_file
from lime.lime_text import LimeTextExplainer
from typing import List, Callable

class Explain():
    def __init__(self, predict:Callable, class_names:List[str]):
        """
        Description:
        
        Arguments:
            predict: Callable function predicting an input
            class_names (optional): Description of the classes
        """
        
        self.class_names = class_names
        self._predict = predict
        self.explainer = LimeTextExplainer(class_names=self.class_names)
        self.result = None
    
    def run(self, text:str, num_features:int=6):
        # run explain on tokens
        self.result = self.explainer.explain_instance(text, self._predict, num_features=num_features).as_list()
        return self.result
     
if __name__ == "__main__":

    # Disable TF Log Level
    from os import environ
    environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  

    #Load Model
    model = load_ml_model_from_file('models/LemmaTfIdfNNClassifierTraining.pkl')
    model.verbose=False
    
    #CHANGE model.predict to predict_lime_bypass IF BYPASS NEEDED
    text = "Life: Life Of Luxury: Elton John’s 6 Favorite Shark Pictures To Stare At During Long, Transcontinent..."

    explain = Explain(predict=model.predict, class_names = ['No Fake News', 'Fake News'])
    result = explain.run(text)

    #print results
    print(f'Lime Prediction for text: \"{text}\"\nis - {sum([r[1] for r in result])} - because\n{result}')