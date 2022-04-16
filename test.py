import spacy
nlp = spacy.load('en_core_web_sm')
from anchor.anchor_text import AnchorText
from classes.ml_file_loader import load_ml_model_from_file
from classes.custom_logging import Logger

log = Logger(verbose=True)

text = 'Jackie Mason: Hollywood Would Love Trump if He Bombed North Korea over Lack of Trans Bathrooms (Exclusive Video)'
text2 = 'Sanders Asks Obama To Intervene In Dakota Access Pipeline Dispute while here'
text3 = 'Trump Picks Mick Mulvaney, South Carolina Congressman, as Budget Director'
text4 = 'Trump'
model = load_ml_model_from_file('models/LinearSvcClassifierTraining.pkl')
model.verbose = False
def predict(X):
    return model.predict(X, transform_to_labels=True)
res = model.predict(text4)
res2 = model.predict(text4, transform_to_labels=True)
print(res, res2)

from lime.lime_text import LimeTextExplainer
ts =  log.get_timestamp()
explainer = LimeTextExplainer()
result = explainer.explain_instance(text, model.predict, num_features=2).as_list()
duration = log.get_duration_str(timestamp_explain)
print(result)
print(duration)

# explainer = AnchorText(nlp, ['0', '1'], use_unk_distribution=True)
# exp = explainer.explain_instance(text, predict, threshold=0.95)
# print('Anchor: %s' % (' AND '.join(exp.names())))
# print('Precision: %.2f' % exp.precision())
# print('\n'.join([x[0] for x in exp.examples(only_same_prediction=True)]))