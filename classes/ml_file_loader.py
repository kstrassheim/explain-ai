from pickle import load, dump

def load_ml_model_from_file(ml_model_file_path:str):
    with open(ml_model_file_path,'rb') as infile:
        model = load(infile)
    return model

def save_ml_model_to_file(model, ml_model_file_path:str):
    model.clear_cache()
    with open(ml_model_file_path,'wb') as outfile:
        dump(model,outfile)
        