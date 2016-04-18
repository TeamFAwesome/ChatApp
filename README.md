# ChatApp #
The chat app that integrates with EIES security as a demo.

## Setup Server ##
```
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Setup Client ##
```
python3 -m http.server 9999
```
Then just navigate your browser to localhost:9999

