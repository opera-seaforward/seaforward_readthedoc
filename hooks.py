import datetime

def on_config(config):
    year = datetime.datetime.now().year
    config.extra['year'] = year
    return config
