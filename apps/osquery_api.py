import os
import binascii
import json
from datetime import datetime
from uuid import uuid4
from bottle import Bottle, request, response, abort
from . import db

# TODO: node_key check decorator
# TODO: check parameter escape
app = Bottle()
response.content_type = 'text/plain'


@app.route('/osquery/enroll', method='POST')
def enroll():  # TODO: autotag based on tag_rules
    "enroll a new osquery client"
    def _get_bussiness_unit(enroll_secret):
        bu_table = db['bussiness_unit']
        return bu_table.find_one(secret=enroll_secret)

    def _create_node_key():
        return binascii.b2a_hex(os.urandom(16))

    # TODO: check if already enrolled
    def _insert_new_client(node_key, hostname, bussiness_unit):
        osq_clients = db['osquery_client']
        osq_clients.insert(dict(hostname=hostname, uuid=str(uuid4()),
                                node_key=node_key, bussiness_unit_id=bussiness_unit['id'],
                                registered_date=datetime.now()))

    req = request.json
    print("got enrollment request from: {}".format(req['host_identifier']))
    b_unit = _get_bussiness_unit(req['enroll_secret'])
    if b_unit:
        node_key = _create_node_key()
        _insert_new_client(node_key, req['host_identifier'], b_unit)
        print("client {} enrolled sucessfully.".format(
            req['host_identifier']))
        response_body = {
            "node_key": node_key,
            "node_invalid": "false"
        }
        return response_body
    else:
        return abort(401, "enrollment secret invalid")


@app.route('/osquery/config', method='POST')
def config():
    "deploy config file based on bussiness unit"
    def _get_client(node_key):
        "get bussiness unit assigned to specific client"
        client_table = db['osquery_client']
        return client_table.find_one(node_key=node_key)

    def _get_client_tags(client):
        "return tag ids assigned to a given client"
        tags_table = db['osquery_client_tag']
        tag_id = []
        for tag in tags_table.find(osqueryclient_id=client['id']):
            tag_id.append(tag['id'])
        return tag_id

    def _get_options(client):
        "get bussiness unit specific options"
        client_config_table = db['client_config']
        options = client_config_table.find_one(
            bussiness_unit_id=client['bussiness_unit_id'])
        if not options:
            options = client_config_table.find_one(name="default")
        return json.loads(options['template_config'])

    # TODO: make sure queries not duplicated if multiple tags assigned
    def _get_event_quieries(tags):
        "get client specific quieries"
        ids = []
        for row in db['event_query_tag'].find(tag_id=tags):
            ids.append(row['id'])
        event_queries = db['event_query'].find(
            enabled=1, id=ids)  # TODO: test what if tag=None
        enabled_queries = {}  # TODO: append untagged queries
        for query in event_queries:
            sql = {'query': str(query['value']),
                   'interval': str(query['interval'])}
            enabled_queries[str(query['name'])] = sql
        return enabled_queries

    node_key = request.json['node_key']
    client = _get_client(node_key)
    print("config request from: {}".format(client['hostname']))
    client_tags = _get_client_tags(client)
    options = _get_options(client)
    schedule = _get_event_quieries(client_tags)
    response_body = {'options': options}
    if schedule:  # append to config only if not empty
        response_body['schedule'] = schedule
    print response_body
    return response_body


@app.route('/osquery/log', method='POST')
def log_query_result():  # TODO: send to redis
    "receive logs and query results from client"
    print("log received:")
    print(request.json)
    return ""


@app.route('/distributed/read', method='POST')
def distributed_read():
    "deploy distributed queries to client"
    print("DISTRIBUTED READ:")
    print(request.json)
    return ""


@app.route('/distributed/write', method='POST')
def distributed_write():
    "receive distributed query result"
    print("DISTRIBUTED WRITE")
    print(request.json)
    return ""
