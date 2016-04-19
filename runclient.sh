#!/bin/sh -e
cd `dirname $0`
if ! which python | grep -q "`pwd`"; then
  virtualenv venv -p python3 || true
fi
. venv/bin/activate
pip install -r requirements.txt --upgrade
python app.py &
pid=$!
trap "if ps aux | grep $pid | grep -qv grep; then echo 'Killing $pid'; kill -9 $pid && wait $pid || true; fi" EXIT TERM INT
python -m http.server 9999 || true
