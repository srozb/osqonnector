from bottle import Bottle, request, response, abort
import json


app = Bottle()
response.content_type = 'text/plain'

def target_print(buf):
    print ("log received (node_key:{}):".format(buf['node_key']))
    print json.dumps(buf, indent=4, sort_keys=True)

@app.route('/osquery/log', method='POST')
def log_query_result():
    "receive logs and query results from client"
    target_print(request.json)
    return ""
