from bottle import Bottle, request

app = Bottle()


@app.route('/osquery/enroll', method='POST')
def enroll():
    print("ENROLLMENT REQUEST:")
    print(request.json)
    return "thx"
