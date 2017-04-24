from bottle import Bottle, response, template

app = Bottle()


@app.route('/static/osquery.flags')
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
