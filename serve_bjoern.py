#!/usr/bin/env python2

from os import getpid
import bjoern
from bottle import Bottle
from apps import healthchecker, static_srv, enroller, flagmaker, indexer

HOST = 'localhost'
PORT = 8000
INSTALLED_APPS = (healthchecker, static_srv, enroller, flagmaker, indexer)

osqonnector = Bottle()
for app in INSTALLED_APPS:
    osqonnector.merge(app.app)

print("about to serv the following apps:")
for app in INSTALLED_APPS:
    print(" * {}".format(app.__name__))
print("[{}]: ready to serv ({}:{})".format(getpid(), HOST, PORT))
try:
    bjoern.run(osqonnector, HOST, PORT, reuse_port=True)
except KeyboardInterrupt:
    print("bye.")
