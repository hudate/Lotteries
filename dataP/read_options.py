import os
import yaml

from settings import BASE_DIR

yaml_file = os.sep.join([BASE_DIR, 'dataB', 'options.yaml'])


def ro():
    with open(yaml_file, 'r', encoding='utf-8') as f:
        setting = f.read()
    return yaml.load(setting, Loader=yaml.FullLoader)