# DISABLE ALL TF LOG !!! HAS TO BE SET AT EVERY POSSIBLE STARTUP FILE AT BEGINNING WHYEVER
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# LOAD Environment Variables
from os import getenv
from dotenv import load_dotenv
from typing import List
load_dotenv()

PREPROCESSING_TARGET_FILE_PATH:str = getenv('PREPROCESSING_TARGET_FILE_PATH', 'datasets/data.csv')
PREPROCESSING_RAW_SOURCE_TRAIN_PATH:str = getenv('PREPROCESSING_RAW_SOURCE_TRAIN_PATH', 'datasets/raw/train.csv')
PREPROCESSING_RAW_SOURCE_TEST_PATH:str = getenv('PREPROCESSING_RAW_SOURCE_TEST_PATH', 'datasets/raw/test.csv')
PREPROCESSING_RAW_SOURCE_TEST_LABEL_PATH:str = getenv('PREPROCESSING_RAW_SOURCE_TEST_LABEL_PATH', 'datasets/raw/submit.csv')
PREPROCESSING_RAW_SOURCE_ID_FIELD_NAME:str = getenv('PREPROCESSING_RAW_SOURCE_ID_FIELD_NAME', 'id')
PREPROCESSING_LEMMATIZE_FIELD_NAMES:List[str] = getenv('PREPROCESSING_LEMMATIZE_FIELD1_NAME', 'title,text').split(',')
PREPROCESSING_LEMMATIZE_SUFFIX_NAME:str = getenv('PREPROCESSING_LEMMATIZE_SUFFIX_NAME', '_lemma')

VERBOSE:bool = getenv('VERBOSE', 'True').lower() == 'true'
RETURN_STD_OUT:bool = getenv('RETURN_STD_OUT', 'True').lower() == 'true'

from time import time, strftime, gmtime
import pandas as pd
import spacy
import multiprocessing as mp
import types
nlp = spacy.load("en_core_web_sm")

from classes.custom_logging import Logger

def preprocess_text(text:str)->List:
    tokenize = nlp(text)
    #Lemmatize and remove stop words
    return [x.lemma_.lower() for x in tokenize if not x.is_stop]

def data_preprocessing(target_file_path:str, data_filter_func:types.FunctionType = None, verbose = False):
    logger = Logger(verbose)
    # concat test labels and data into 1 dataframe
    # concat train and test data together to use sklearn train test split and cross validation
    data = pd.concat([pd.read_csv(PREPROCESSING_RAW_SOURCE_TRAIN_PATH, index_col=PREPROCESSING_RAW_SOURCE_ID_FIELD_NAME), pd.concat([pd.read_csv(PREPROCESSING_RAW_SOURCE_TEST_PATH, index_col=PREPROCESSING_RAW_SOURCE_ID_FIELD_NAME), pd.read_csv(PREPROCESSING_RAW_SOURCE_TEST_LABEL_PATH, index_col=PREPROCESSING_RAW_SOURCE_ID_FIELD_NAME)], axis=1)])
    
    # Apply external filter if available
    if data_filter_func is not None: data = data_filter_func(data)

    # Pre lemmatize is not required any more
    # Start multi processor preprocessing
    # timestamp_start_lemma = logger.get_timestamp()
    # with mp.Pool(mp.cpu_count()) as pool:
    #     for lemmatize_field_name in PREPROCESSING_LEMMATIZE_FIELD_NAMES:
    #         data[f'{lemmatize_field_name}{PREPROCESSING_LEMMATIZE_SUFFIX_NAME}'] = pool.map(preprocess_text, data[lemmatize_field_name].astype(str))
    # logger.log_duration("Lemmatize Duration", timestamp_start_lemma)

    #save to csv
    if target_file_path is not None : data.to_csv(target_file_path, sep=',')
    return len(data)

# execute only if not run by external file
if __name__ == "__main__":
    # WRITE A STD OUT
    res = data_preprocessing(PREPROCESSING_TARGET_FILE_PATH, None, verbose=VERBOSE)
    if RETURN_STD_OUT: print(res)
