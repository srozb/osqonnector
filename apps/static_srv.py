from bottle import Bottle, static_file

app = Bottle()


@app.route('/static/haproxy.crt')
def deploy_haproxy_pem():
    "serve haproxy.crt static file"
    return static_file('haproxy.crt', root='./static/cert')
