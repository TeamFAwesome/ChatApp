# ChatApp #
The chat app that integrates with EIES security as a demo.
This app was based on some python websocket starter code found here,
http://iot-projects.com/index.php?id=websocket-a-simple-example

## Dependencies ##
On Ubuntu:
```
sudo apt-get install python-virtualenv python3-dev
```

On other distros:
after installing python-virtualenv, play whack-a-mole until ./runclient.sh no longer errors :-P


## Setup+Run Chat client ##
```
./runclient.sh
```
Then just navigate your browser to localhost:9999

## Setup+Run Centralized Chat Server ##
```
./runserver.sh
```
The chat server is running at the endpoint specified in ChatApp.js, and would need reconfiguration to run elsewhere.

## Under the Hood of EIESWrapper and its integration ##

tl;dr: EIESWrapper is used directly by ChatApp.js (localhost-only websockets). All message crypto happens on the localhost before transmission.

EIESWrapper.py is a trivial requests session wrapper to expose the EIES api calls in python
It can be used directly on a CLI, or integrated into python code.
One of app.py's WebSocket servers handles EIESWrapper calls introspectively, not caring which args are passed or which functions are being called.
EIESWrapper.js defines a JavaScript interface for all of the EIESWrapper functions, with the only caveat being that all of the calls require a callback function to be passed in additional to the other arguments, as the 2-hops of WebSockets between a call and its return make the calls asynchronous.
