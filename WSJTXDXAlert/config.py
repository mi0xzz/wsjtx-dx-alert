import yaml
import logging

LOG_LEVEL = logging.DEBUG
LOG_FILE = '/tmp/wsjtx-dx-alert.log'

with open('settings.yaml', 'r') as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)
    print(settings["BANDS"])
