'''
Paralysis C2 source
written by Null
'''

import json, os

from src.core import Core
from src.logging import *

class Config:
    # host and port to listen on
    host,port = None,None
    # 0 is simple, 1 is medium 2 is hard
    captchaEnabled, captchaType = True, 2

    # max login attempts
    max_tries = 5

    def make() -> None:
        '''
        Makes the default config if none is found
        '''

        if not os.path.isfile('assets/config.json'):
            with open('assets/config.json', 'w+') as fd:
                fd.write(Core.defaultConfig)
            logging.info('Config created')
        else:
            logging.error('Config file already exists. Not overwriting.')

    def load() -> None:
        '''
        Attempts to load the config
        '''

        if not os.path.isfile('assets/config.json'):
            logging.error('Config file not found, making one.')
            Config.make()

        with open('assets/config.json') as fd:
            config = json.loads(fd.read())
        
        Config.host = config['c2']['host']
        Config.port = config['c2']['port']
        Config.captchaEnabled = config['captcha']['enabled']
        Config.captchaType = config['captcha']['type']
        Config.max_ties = config['login']['max_tries']