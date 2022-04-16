
def process_keras_default_unit_test_main_call():    
    from os import getenv, environ
    from dotenv import load_dotenv
    
    # Set TF Log Level
    load_dotenv()
    environ['TF_CPP_MIN_LOG_LEVEL'] = f"{int(getenv('UNIT_TEST_TF_LOG_LEVEL', '3'))}" 
    UNIT_TEST_VERBOSE:bool = getenv('UNIT_TEST_VERBOSE', 'False').lower() == 'true'

    #LOG SETTINGS
    import warnings
    if UNIT_TEST_VERBOSE == False: 
        warnings.filterwarnings("ignore")
        warnings.filterwarnings("ignore", category=DeprecationWarning)