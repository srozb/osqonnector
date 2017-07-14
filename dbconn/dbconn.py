import dataset
import config

def get_connection():
        return dataset.connect(config.DB_URL)
