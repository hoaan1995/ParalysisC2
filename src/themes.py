'''
Paralysis C2 source
written by Null
'''

import json, os
from glob import glob
from colorama import Fore, init

init() # initalize colorama

from src.database import Database
from src.core import Core
from src.colors import Colors

class Theme:
    themes = {}
    themeNames = [] # just a list holding juuust the theme names

    def parse(theme:str, raw:dict) -> dict:
        '''
        Parses the theme info a easier to access dictionary
        '''
 
        parsed = {
            'name': raw['name'],
            'author': raw['author'],
            'prefix': '' if not raw['prefix'] else raw['prefix']
        }

        return parsed

    def load() -> list:
        '''
        Returns all themes in a list
        '''

        output = []
        for theme in glob('assets/themes/*'):
            theme = theme.split('/')[-1].lower().split('\\')[-1].lower()
            with open(f'assets/themes/{theme}/{theme}.json', buffering=(16*1024*1024)) as fd:
                data = json.loads(fd.read())

                parsed = Theme.parse(theme, data)
                output.append(parsed)
        
        return output
        
    def loadTheme(theme:str) -> dict:
        '''
        Returns the parsed info of a specific theme
        '''

        output = {}
        for theme_directory in glob('assets/themes/*'): # load the entire folder
            if theme.lower() in theme_directory.split('/')[-1].lower(): # check if the folder actually exists
                with open(f'assets/themes/{theme}/{theme}.json', buffering=(16*1024*1024)) as fd: # open the theme config
                    output = Theme.parse(theme, json.loads(fd.read()))
        
        return output
    
    def getTheme(username:str) -> str:
        '''
        Gets the users selected theme
        '''

        result = Database().lookupUser(username)
        return result['theme'] if result != None else ''
    
    def validTheme(name:str) -> bool:
        '''
        Checks if a theme exists
        '''

        themeNames = [theme.split('/')[-1].lower().split('\\')[-1].lower() for theme in glob('assets/themes/*')]

        return name.lower() in themeNames