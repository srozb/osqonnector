from bottle import Bottle, template

app = Bottle()


@app.route('/')
def index():
    return template('templates/index')
