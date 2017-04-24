#!/usr/bin/env python2

from bottle import default_app, route, static_file, request, template, response
from random import randint
from os import getpid
import bjoern


@route('/healthcheck')
def healthcheck():
    print("Got healthcheck.")
    return "<h2>[PID:{}] ready to serve.</h2>".format(getpid())


@route('/static/haproxy.crt')
def deploy_haproxy_pem():
    return static_file('haproxy.crt', root='./static/cert')


@route('/static/osquery.flags')
def deploy_flag_file():
    params = {
        'osquery_path': 'C:\\ProgramData\\osquery',
        'enroll_tls_endpoint': '/osquery/enroll',
        'windows_event_channels': 'Microsoft-Windows-Sysmon/Operational',
        'distributed_interval': '180',
        'config_tls_refresh': '300',
    }
    response.content_type = 'text/plain'
    return template('templates/flag_file', **params)


@route('/osquery/enroll', method='POST')
def enroll():
    print("ENROLLMENT REQUEST:")
    print(request.json)
    return "thx"


print("[{}]: ready to serv".format(getpid()))
bjoern.run(default_app(), 'localhost', 8000, reuse_port=True)
