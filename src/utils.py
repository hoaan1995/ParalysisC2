'''
Paralysis C2 source
written by Null
'''

import subprocess, os, socket, time
from colorama import Fore, init
from tabulate import tabulate
from datetime import datetime

from src.check import Check
from src.database import Database
from src.core import Core
from src.themes import Theme
from src.colors import Colors
from src.logging import *

class Utils():
    def __init__(self):
        self.ansiClear = b'\033[2J\033[H'
        self.devnull = open(os.devnull)
    
    def themeList(self, theme:str or None=None, clist:list=[], about_split:str=': ') -> str:
        '''
        Returns the specified list in the theme format
        '''

        final = []
        for item in clist:
            name, info = item # we only parse the name and the information here
            match theme.lower():
                case 'default':
                    line = './'
                    line += '{0: <39}'.format(name)
                    line += '| '
                    line += info

                case 'senpai':
                    line = '\033[36m |\033[97m !* '
                    line += '{0: <39}'.format(name)
                    line += '\033[36m| '
                    line += '{0: <21}'.format(info)
                    line += '\033[36m|'
                
                case _:
                    line = f'{name}{about_split}{info}' # default one

            final.append(line)    
        return '\n'.join(final)
    
    def banIP(self, ip:str) -> bool:
        '''
        Completely bans an IP from connecting using iptables
        '''
        if not Check().isipv4(ip): # if its an invalid IP
            return False

        subprocess.Popen(f'iptables -I INPUT -s {ip} -j DROP', stdout=self.devnull, shell=True)  
        return True      
    
    def clear(self, client:socket.socket) -> None:
        '''
        Clears the terminal
        '''
        try: client.send(self.ansiClear)
        except: client.send(b'\r\n'*100) # backup method, sloppy but it works
    
    def title(self, client:socket.socket, text:str) -> None:
        '''
        Sets the terminal title
        '''
        client.send(f'\33]0;{text}\a'.encode())
    
    def send(self, client:socket.socket, data:str, escape:bool=True, reset:bool=True, slow_write:bool=False, write_delay:int or float=0.2) -> None:
        '''
        Sends data over a specified socket
        '''

        if slow_write:
            for char in data:
                client.send(char.encode())
                time.sleep(write_delay)
            if reset: client.send(Fore.RESET.encode())
            if escape: client.send(b'\r\n')

        else:
            client.send(data.encode())
            if reset: client.send(Fore.RESET.encode())
            if escape: client.send(b'\r\n')
    
    def recv(self, client:socket.socket, bufsize:int=2048, timeout:int=20) -> str:
        '''
        Listens on the specified socket
        '''
        data = None
        while 1:
            data = client.recv(bufsize).decode().strip()
            if not data or data == ' '*len(data): # checks for any empty lines too
                continue
            break
        return data
    
    def tableify(self, headers:list, items:list, username:str=None) -> str:
        '''
        Makes a nice table
        '''

        if not username: # no username supplied, default colors go!
            main_color = Fore.LIGHTBLUE_EX
        else:
            main_color = Colors().HEXtoANSI(Theme.loadTheme(Theme.getTheme(username))['main_clr'])

        table = tabulate(items, headers, tablefmt="simple").replace('-', f'{main_color}-{Fore.RESET}')

        return table
    
    def convert_timestamp(self, timestamp:int) -> object:
        '''
        Calculates the timestamps back into the original date, and returns the days
        '''

        expiry = str(datetime.fromtimestamp(timestamp))
        now = datetime.now()
        year = int(expiry.split("-")[0])
        month = int(expiry.split("-")[1])
        day = int(expiry.split("-")[2].split(" ")[0])
        expiry_ = datetime(year, month, day)

        duration = expiry_ - now
        return duration.days
    
    def shutdown(self) -> None:
        '''
        Shuts everything down
        '''

        logging.info('Shutting down')

        self.devnull.close() # closes the file descriptor
        Database().disconnect() # saves and closes the db
        Core.isAlive = False # kills any loops
        exit() # shuts doen