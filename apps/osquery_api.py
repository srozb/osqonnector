import os
import binascii
import json
import re
import redis
from ipaddress import ip_address, ip_network
from datetime import datetime
from uuid import uuid4
from bottle import Bottle, request, response, HTTPResponse
from . import db

# TODO: node_key check decorator
# TODO: check parameter escape
app = Bottle()
response.content_type = 'application/json'
r = redis.StrictRedis(host='localhost', port=6379, db=0)


def _get_client():
    "get bussiness unit assigned to specific client"
    client = db['osquery_client'].find_one(node_key=request.json['node_key'])
    if not client:
        print "[W] Node key: {} not in db. Asking to reenroll.".format(
            request.json['node_key'])
        raise HTTPResponse(status=200, content_type='application/json',
                           body='{"node_invalid": true}\n')
    return client


def _get_client_tags(client):
    "return tag ids assigned to a given client"
    tags_table = db['osquery_client_tag']
    tag_id = []
    for tag in tags_table.find(osqueryclient_id=client['id']):
        tag_id.append(tag['tag_id'])
    return tag_id


def _update_client_communication(client):
    "update last_communication datetime"
    client_table = db['osquery_client']
    client_table.update(
        dict(id=client['id'], last_communication=datetime.utcnow()), ['id'])


def _enrich_message(client, message):
    client_data = {'client_id': client['id'], 'host_identifier': client['hostname'],
    'uuid': client['uuid'], 'version': client['version'], 'ip': client['ip'],
    'bu_id': client['bussiness_unit_id']}
    return {'client': client_data, 'message': message}

@app.route('/osquery/enroll', method='POST')
def enroll():  # TODO: autotag based on tag_rules
    "enroll a new osquery client"
    def _get_bussiness_unit(enroll_secret):
        bu_table= db['bussiness_unit']
        return bu_table.find_one(secret=enroll_secret)

    def _generate_node_key():
        return binascii.b2a_hex(os.urandom(16))

    # TODO: check if already enrolled
    def _insert_new_client(node_key, hostname, bussiness_unit, ip, useragent):
        osq_clients= db['osquery_client']
        return osq_clients.insert(dict(hostname=hostname, uuid=str(uuid4()),
                                       node_key=node_key,
                                       bussiness_unit_id=bussiness_unit['id'],
                                       registered_date=datetime.utcnow(),
                                       last_communication=datetime.utcnow(),
                                       ip=ip, version=useragent,
                                       last_distributed_id=0))

    def _auto_assign_tags():
        "assign tags based on TagAssignmentRules"
        def _rule_matches(rule):
            if rule['type'] == 'IP':
                return ip_address(unicode(client_ip)) == ip_address(rule['value'])
            elif rule['type'] == 'SUBNET':
                return ip_address(unicode(client_ip)) in ip_network(rule['value'])
            elif rule['type'] == 'REGEX':
                return re.match(rule['value'], req['host_identifier'])
            print "unsupported rule type"
        for rule in db['osquery_tagassignmentrules'].find(enabled=1):
            if _rule_matches(rule):
                db['osquery_client_tag'].insert(dict(osqueryclient_id=client_id,
                                                     tag_id=rule['tag_id']))
    req= request.json
    print("got enrollment request from: {}".format(req['host_identifier']))
    b_unit= _get_bussiness_unit(req['enroll_secret'])
    if not b_unit:
        return {"node_invalid": True}
    node_key= _generate_node_key()
    client_ip= request.remote_addr
    useragent= request.get_header("user-agent")
    client_id= _insert_new_client(
        node_key, req['host_identifier'], b_unit, client_ip, useragent)
    _auto_assign_tags()
    print("client {} enrolled sucessfully.".format(
        req['host_identifier']))
    return {
        "node_key": node_key,
        "node_invalid": False
    }


@app.route('/osquery/config', method='POST')
def config():
    "deploy config file based on bussiness unit"

    def _get_options(client):
        "get bussiness unit specific options"
        client_config_table= db['client_config']
        options= client_config_table.find_one(
            bussiness_unit_id=client['bussiness_unit_id'])
        if not options:
            options= client_config_table.find_one(name="default")
        return json.loads(options['template_config'])

    # TODO: make sure queries not duplicated if multiple tags assigned
    def _get_event_quieries(tags):
        "get client specific quieries"
        ids= []
        for row in db['event_query_tag'].find(tag_id=tags):
            ids.append(row['id'])
        event_queries= db['event_query'].find(
            enabled=1, id=ids)  # TODO: test what if tag=None
        enabled_queries= {}  # TODO: append untagged queries
        for query in event_queries:
            sql= {'query': str(query['value']),
                   'interval': str(query['interval'])}
            enabled_queries[str(query['name'])]= sql
        return enabled_queries

    client= _get_client()
    _update_client_communication(client)
    print("config request from: {}".format(client['hostname']))
    client_tags= _get_client_tags(client)
    options= _get_options(client)
    schedule= _get_event_quieries(client_tags)
    response_body= {'options': options}
    if schedule:  # append to config only if not empty, TODO: remove if not needed
        response_body['schedule']= schedule
    return response_body


@app.route('/osquery/log', method='POST')
def log_query_result():
    "receive logs and query results from client"
    client= _get_client()
    # print json.dumps(request.json, indent=4, sort_keys=True)
    message= _enrich_message(client, request.json)
    r.publish('osquery_log', message)
    return {"node_invalid": False}


@app.route('/osquery/distributed/read', method='POST')
def distributed_read():
    "deploy distributed queries to client"
    def _get_query_ids_by_tag(tags):
        ids= []
        for row in db['distributed_query_tag'].find(tag_id=tags):
            ids.append(row['id'])
        return ids

    def _update_last_distributed_id(query_id):
        client_table= db['osquery_client']
        client_table.update(
            dict(id=client['id'], last_distributed_id=query_id), ['id'])

    def _get_distributed_queries(tags):
        "get client specific quieries"
        ids= _get_query_ids_by_tag(tags)
        distributed_queries= db['distributed_query'].find(
            enabled=1, id=ids, order_by='id')  # BUG: not getting anything if tag=2
        query_id= 0
        enabled_queries= {}  # TODO: append untagged queries
        for query in distributed_queries:
            if query['id'] > client['last_distributed_id']:
                enabled_queries[query['name']]= query['value']
                query_id= query['id']
        # BUG: if disabled distributed queries
        if query_id > client['last_distributed_id']:
            _update_last_distributed_id(query_id)
        return enabled_queries

    client= _get_client()
    _update_client_communication(client)
    client_tags= _get_client_tags(client)
    queries= _get_distributed_queries(tags=client_tags)
    # print("get distributed queries (host:{})".format(client['hostname']))
    response_body= {'queries': queries}
    response_body['node invalid']= False
    return response_body


@app.route('/osquery/distributed/write', method='POST')
def distributed_write():
    "receive distributed query result"
    client= _get_client()
    # print("distributed query result received:")
    # print json.dumps(request.json, indent=4, sort_keys=True)
    message= _enrich_message(client, request.json)
    r.publish('osquery_distributed', message)
    return {"node_invalid": False}
