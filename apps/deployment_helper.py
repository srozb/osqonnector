from bottle import Bottle, response, template

app = Bottle()


@app.route('/static/osquery.flags')
def deploy_flag_file():  #TODO: generate base on templates/os version
    "serve flag file for easy deployment"
    params = {
        'osquery_path': 'C:\\ProgramData\\osquery',
        'enroll_tls_endpoint': '/osquery/enroll',
        'windows_event_channels': 'Microsoft-Windows-Sysmon/Operational',
        'distributed_interval': '180',
        'config_tls_refresh': '300',
    }
    response.content_type = 'text/plain'
    return template('templates/flag_file', **params)


@app.route('/osquery/generate_secret')
def generate_secret():  # TODO: generate secretfile based on bussiness unit.
    "generate secret file for further use"
    response.content_type = 'text/plain'
    SECRET = 'eyJtb2R1bGUiOiJ6ZW50cmFsLmNvbnRyaWIub3NxdWVyeSIsImJ1X2s'
    SECRET += 'iOiI1YWE2OGRlOCJ9:1ch5al:G-Zd7VAs4s9DA4_7FPdYu3sGklc$SERIAL$'
    return SECRET + '\n'
