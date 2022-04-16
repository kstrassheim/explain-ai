from django.http import JsonResponse
from django.urls import path, re_path
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
import json
import uuid
from datetime import datetime

import sklearn
import classes.lime_extensions.lime_extensions as le
from lime.lime_text import LimeTextExplainer
from numpy.core.fromnumeric import argmax
from .item import appendItem
from .auth import get_access_token_from_request, process_authorization
from anchor.anchor_text import AnchorText
import spacy
nlp = spacy.load("en_core_web_sm")

urls = [] 

# Remark the overloading of string parameter over same url
async def post_explain(request):
    if request.method == "POST":
        access_token = get_access_token_from_request(request)
        login_name = process_authorization(access_token)["login"]
        # get params
        post_data = json.loads(request.body.decode("utf-8"))
        item = post_data.get("item")

        # set item name
        item["name"] = item["text"][0:50].strip() if len(item["text"]) > 50 else item["text"].strip()

        # init ml model
        from classes.custom_logging import Logger
        log = Logger(verbose=False)
        timestamp_ml = log.get_timestamp()
        from classes.ml_file_loader import load_ml_model_from_file

        # Load and init AI Model to explain
        from os import environ
        environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # DEACTIVATE while tensorflow log
        modelfile = ''
        if (item["model"] == "TfIdf"): modelfile = 'LemmaTfIdfNNClassifierTraining'
        elif (item["model"] == "LSTM"): modelfile = 'LstmClassifierTraining'
        elif (item["model"] == "BERT"): modelfile = 'DistilbertClassifierTraining'
        elif (item["model"] == "SVM"): modelfile = 'LinearSvcClassifierTraining'
        else: raise TypeError("ML Model not found")
        model = load_ml_model_from_file(f'models/{modelfile}.pkl')
        model.verbose = False
        model_prediction_label = model.predict(item["text"], transform_to_labels=True).tolist()
        model_prediction = model.predict(item["text"])
        model_prediction = model_prediction.tolist()## have to run predict to init model otherwise it will be slow on first load
        duration_init_ml_str = log.get_duration_str(timestamp_ml)
        duration_init_ml = log.get_duration(timestamp_ml)
        log.log_duration("Init ML Duration", timestamp_ml)

        #Process LIME
        error_measure_mapping = {
                'MAE':sklearn.metrics.mean_absolute_error,
                'MSE':sklearn.metrics.mean_squared_error
            }
        from lime.lime_text import LimeTextExplainer
        timestamp_explain = log.get_timestamp()
        timestamp_explain_lime = log.get_timestamp()

        item["result"] = {}
        item['result']['name'] = item['explainer']['name']
        item['result']['modelPredictionLabels'] = model_prediction_label
        item['result']['modelPrediction'] = model_prediction
        item['result']['durationInitMl'] = duration_init_ml
        if(item['explainer']['name'] == 'LIME'):
            explainer = LimeTextExplainer()
            explain_result = explainer.explain_instance(item["text"], model.predict, num_features=item['explainer']["num_features"], num_samples=item['explainer']["num_samples"])
            explain_result_list = explain_result.as_list()
            explain_result_mapped = le.map_result_to_string(explain_result)

            item["result"]["explainer_result"] = explain_result_list
            item["result"]["explainer_result_string_mapped"] = {
                "strings":explain_result_mapped[0],
                "values":explain_result_mapped[1]
            }
            item['result']['explainer_score'] = explain_result.score
            item['result']['sample_size'] = item['explainer']["num_samples"]
        elif(item['explainer']['name'] == 'IterativeLIME'):

            explainer = le.IterativeLimeTextExplainer(min_samples = item['explainer']['min_samples'],
                                                      max_samples = item['explainer']['max_samples'],
                                                      step_size = item['explainer']['step_size'],
                                                      error_measure=error_measure_mapping[item['explainer']['distance_metric']],
                                                      error_cutoff=item['explainer']['error_cutoff']
            )
            explain_result = explainer.explain_instance(item["text"], model.predict, num_features=item['explainer']["num_features"])
            explain_result_list = explain_result.as_list()
            explain_result_mapped = le.map_result_to_string(explain_result)

            item["result"]["explainer_result"] = explain_result_list
            item["result"]["explainer_result_string_mapped"] = {
                "strings":explain_result_mapped[0],
                "values":explain_result_mapped[1]
            }
            item['result']['explainer_score'] = explain_result.score
            item['result']['sample_size'] = len(explainer.data)
            
        elif(item['explainer']['name'] == 'MultiStepLIME'):
            
            explainer = le.MultiLevelSampling(min_samples = [item['explainer']['min_samples'][0], item['explainer']['min_samples'][1]],
                                                      max_samples = [item['explainer']['max_samples'][0], item['explainer']['max_samples'][1]],
                                                      step_size = [item['explainer']['step_size'][0], item['explainer']['step_size'][1]],
                                                      error_measure=[error_measure_mapping[item['explainer']['distance_metric'][0]], error_measure_mapping[item['explainer']['distance_metric'][0]]],
                                                      error_cutoff=[item['explainer']['error_cutoff'][0], item['explainer']['error_cutoff'][1]],
                                                      split_expression=[le.split_sentence, '\W+']
            )
            if item['explainer']['select'] == 'Combined':
                explainer.individual = False
            else:
                explainer.individual = True

            explain_result = explainer.explain_instance(item["text"], model.predict, num_features=item['explainer']["num_features"])


            if item['explainer']['select'] == 'Combined':
                item['result']['explainer_result'] = [
                    explainer.results[0].as_list(),
                    explainer.results[1].as_list()
                ]
                item['result']['explainer_result_string_mapped'] = {
                    'strings':[le.map_result_to_string(explainer.results[0])[0], le.map_result_to_string(explainer.results[1])[0]],
                    'values': [le.map_result_to_string(explainer.results[0])[1], le.map_result_to_string(explainer.results[1])[1]]
                }
            else:
                item['result']['explainer_result'] = explainer.results_combined
                item['result']['explainer_result_string_mapped'] = {
                    'strings': [le.map_multiple_results_to_string(explainer.results_individual[0], explainer.results_combined[0])[0], le.map_multiple_results_to_string(explainer.results_individual[1], explainer.results_combined[1])[0]],
                    'values' : [le.map_multiple_results_to_string(explainer.results_individual[0], explainer.results_combined[0])[1], le.map_multiple_results_to_string(explainer.results_individual[1], explainer.results_combined[1])[1]]
                }

        elif(item['explainer']['name'] == 'Anchor'):
            pass


        duration_explain_lime = log.get_duration(timestamp_explain_lime)
        item['result']['durationExplain'] = log.get_duration(timestamp_explain)
        
        # append metadata
        now = datetime.now().isoformat()
        operation = 'edit'
        if item["id"] == None or item["id"] == -1:
            operation = 'add'
            item["id"] = uuid.uuid1().hex
            item["created"] = now
            item["createdBy"] = login_name
        item["modified"] = now
        item["modifiedBy"] = login_name

        # save item to azure blob
        appendItem(item)

        # send info to other clients
        await get_channel_layer().group_send("item", {
            "type": "item.info",
            "operation": operation,
            "user": login_name,
            "item": item
        })

        # return item
        return await sync_to_async(JsonResponse)(item)
    else:
        raise Exception(f"Method {request.method} not allowed")
urls+=[path('api/explain', post_explain)]


