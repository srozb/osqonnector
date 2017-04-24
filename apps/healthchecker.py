from os import getpid
from bottle import Bottle

app = Bottle()


@app.route('/healthcheck')
def healthcheck():
    print("Got healthcheck.")
    return "<h2>[PID:{}] ready to serve.</h2>".format(getpid())
