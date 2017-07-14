#!/usr/bin/env python2

from os import getpid
import bjoern
from bottle import Bottle
import config
from logger.logger import Logger
from apps import healthchecker, static_srv, osquery_api, deployment_helper, indexer

INSTALLED_APPS = (healthchecker, static_srv, osquery_api,
                  deployment_helper, indexer)

def main():
    l = Logger(__name__)
    osqonnector = Bottle()

    for app in INSTALLED_APPS:
        l.debug("loading {}".format(app.__name__))
        osqonnector.merge(app.app)

    l.debug("[{}]: ready to serv ({}:{})".format(getpid(), config.HOST, config.PORT))
    try:
        bjoern.run(osqonnector, config.HOST, config.PORT,
                   reuse_port=config.REUSE_PORT)
    except KeyboardInterrupt:
        l.info("bye.")

if __name__ == "__main__":
    main()
