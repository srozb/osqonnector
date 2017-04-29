import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('etc/wsgi/apps.conf')

dbms = config.get('main', 'dbms')
if dbms:
    import dataset
    db = dataset.connect(dbms)
