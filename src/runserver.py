#!/usr/bin/env python

import os, sys
from os.path import dirname, realpath, join
from flask_bootstrap import Bootstrap

print(sys.path)
path = join(dirname(realpath(__file__)), "app")

print (path)
print (__file__)
sys.path.append(path)

print(sys.path)
from application import app

if __name__ == '__main__':
    Bootstrap(app)
    app.run(host='0.0.0.0', port=5000)
