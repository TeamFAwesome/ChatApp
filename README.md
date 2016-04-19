# ChatApp #
The chat app that integrates with EIES security as a demo.
This app was based on some python websocket starter code found here,
http://iot-projects.com/index.php?id=websocket-a-simple-example

## Setup Server ##
```
$ virtualenv venv
$ pip install -r requirements.txt
$ source venv/bin/activate
$ python app.py
```

## Setup Client ##
```
$ python3 -m http.server -m 9999
```
Then just navigate your browser to localhost:9999

