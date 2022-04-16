# Explain-AI (2021)
This web-app shows the functionality of the model-agnostic explainable-ai engine LIME on 3 common deep learning text classifiers (BERT, LSTM, TFIDF-NN) for fake news detection. 
A demo of the application can be viewed at https://explain-ai-demo.azurewebsites.net/
## Abstract-Keywords
AI, Explainable-AI, Model-Agnostic Methods, LIME, NLP, Deep Learning, LSTM, BERT, TFIDF, Python Web-application, Progressive-Web-App (PWA), AI-Model-UnitTests

## Technical-Keywords
Python, Tensorflow, Pandas, Numpy, LIME, Spacy, Django ASGI, Django Channels, JavaScript, React, Bootstrap, Chart-JS, Toastr, PWA, JSONL, Azure Web-App, Azure File Storage, Python Unit Tests

## User Manual
1. Install the Application like described in Installation Section
2. Open the website on page home (Default)
3. A login screen from github appears where you have to authenticate. Afterwards you will be redirected to the page again (Disabled in demo)
4. After a short loading you can see your github user profile image as well as a list of explanations which you can select and expand.
5. With the green circle arrow button you can reload the page whenever you want.
6. The blue items are classified as No Fake News while the Red are classified as Fake News
7. You can create a new explanation by click on the blue + button on top (Disabled in demo)
8. You can also select a explanation and click yellow pencil button on top to enter the detail view
9. When you are in detail view you can click on Edit Text below the text to change the prediction text als well the AI-Model and the Explain Parameters. The explanation result will be reseted here.
10. From the edit text mode you can click on Cancel to reload the saved text again or click on Exlain to run a new Explanation on the server (Disabled in demo)
11. You can also delete a explanation by select an item in the home screen and click the red trash button. After confirmation the item will be deleted. (Disabled in demo)
12. For any change from any user you will see toast notifications as well as receive updates on your current list.
13. (Optional) For installing on a mobile device to have an app on your smartphone or tablet open the site on this device and click "Add to Home Screen"

## Installation

__The application is only working properly on Linux (Ubuntu 20.04). The application requres at least 16GB of RAM on the computer to run explanations, and 64GB of RAM and 24GB GPU Ram for training the models__

### For installation
Install python 3.8
Install NodeJS

pip install -r requirements.txt
npm ci

#start venv linux
source venv/bin/activate

### Launch Debug have to start both
npm start
cd ..
python webapp.py runserver

### BUILD and run Prod
### set debug=false in settings.py
npm run-script build
cd ..
python webapp.py collectstatic --noinput 
gunicorn -w 1 -k uvicorn.workers.UvicornWorker --bind=0.0.0.0 --timeout 600 --env DJANGO_SETTINGS_MODULE=webapp_settings webapp_asgi


### VSCode settings.json
{
    "python.pythonPath": "venv/bin/python.exe"
}

#VSCode debug launch.json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
    
        {
            "name": "Launch Chrome",
            "request": "launch",
            "type": "pwa-chrome",
            "url": "http://127.0.0.1:8000",
            "webRoot": "${workspaceFolder}/webapp"
        },
        {
            "name": "Python: Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": [
                "runserver",
                "127.0.0.1:8000"
            ],
            "django": true
        }
    ]
}

## Retraining the models
The training is configured in the train_*.py files
For retraining the models run `python train_[model_name].py`

__for any further info on this project or extended manuals read the documentation in the ./Documentation folder__
