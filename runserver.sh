#!/bin/sh -e
cd `dirname $0`
if ! which python | grep -q "`pwd`"; then
  virtualenv venv_server -p python3 || true
fi
. venv_server/bin/activate
pip install -r requirements.txt --upgrade
python ChatServer.py
