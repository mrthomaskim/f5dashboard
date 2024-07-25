#!/bin/bash

if [ -f helper ]; then
  echo "using helper file"
  source ./helper
else
  echo "using helper.exmaple file"
  source ./helper.example
fi
export FLASK_APP=runserver.py
#export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5010
