'''
Paralysis C2 source
written by Null
'''

import sqlite3, hashlib, os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.core import Core
from src.logging import *

class Database():
    def __init__(self):
        self.db, self.cursor = None, None
        self.connect() # connects to the DB
    
    def login(self, username:str, password:str) -> bool:
        '''
        Checks if the user exists in the database
        '''

        hashed_pw = hashlib.sha512(password.encode()).hexdigest()

        response = self.query('SELECT * FROM users WHERE username=? AND password=?', (username,hashed_pw,)).fetchone()
        return response != None
    
    def query(self, query:str, args:tuple or None=None, commit:bool=False) -> list:
        '''
        Executes a single query
        '''
        with Core.threadLock:
            output = self.cursor.execute(query) if args is None else self.cursor.execute(query, args)

            if commit:
                self.db.commit()
        return output
    
    def queryMany(self, queryList:list, commit:bool=False) -> list:
        '''
        Executes many statements at the same time
        '''
        output = []
        for query, args in queryList:
            with Core.threadLock:
                output.append(self.cursor.execute(query) if args is None else self.cursor.execute(query, args))

        if commit:
            self.db.commit()

        return output
    
    def connect(self) -> None:
        '''
        Connects to the database
        '''
        if not os.path.isfile('assets/database/db.db'):
            logging.error('Database file not found, creating one.')
            self.make()

        self.db = sqlite3.connect("assets/database/db.db", check_same_thread=False)
        self.cursor = self.db.cursor()

        self.cursor.execute("PRAGMA journal_mode = WAL")
        self.cursor.execute("PRAGMA synchronous = OFF")
        self.cursor.execute("PRAGMA cache_size = -40960")
    
    def disconnect(self) -> None:
        '''
        Disconnects from the database
        '''

        self.db.commit()
        self.db.close()
    
    def make(self) -> None:
        '''
        If no database is found, we will make one
        '''
        with open('assets/database/db.db', 'w+') as fd: # first, we create the file
            pass

        self.connect()

        # creates the users table
        self.query('''CREATE TABLE users (username text,
            password text,
            concurrents int,
            concurrents_used int,
            maxtime int,
            cooldown int,
            expiry int,
            vip bool,
            reseller bool,
            admin bool,
            banned bool,
            online bool,
            theme text
        )''', commit=True)

        self.query('CREATE TABLE ipban (ip text)') # creates the ip ban table, used to completely block IPs from connecting
        self.query('CREATE TABLE blacklist (host text)') # creates the blacklist table

        for host in [ # adds some host into the blacklist
            # dns servers
            '1.1.1.1', # cloudflare 1
            '1.0.0.1', # cloudflare 2
            '8.8.8.8', # google 1
            '8.8.4.4', # google 2
            '2001:4860:4860::8888', # google ipv6 1
            '2001:4860:4860::8844', # google ipv6 2
            '208.67.222.222', # opendns 1
            '208.67.220.220', # opendns 2
            '9.9.9.9', # quad9 1
            '149.112.112.112', # quad9 2
            '9.9.9.11', # quad9 3
            '149.112.112.11', # quad9 4
            '9.9.9.10', # quad9 5
            '149.112.112.10', # quad9 6
            '2620:fe::fe', # quad9 ipv6 1
            '2620:fe::9', # quad9 ipv6 2
            '2620:fe::11', # quad9 ipv6 3
            '2620:fe::fe:11', # quad9 ipv6 4
            '2620:fe::10', # quad9 ipv6 5
            '2620:fe::fe:10', # quad9 ipv6 6

            # websites
            'wikipedia',
            'pornhub',
            'xvideos',
            'xnxx',
            'google.com',
            'discord.app'

            # goverments
            '.gov',

            # military
            '.mil',

            # schools
            #'.edu',

            # federal agencies
            'fbi',
            'cia',
            'nsa']: self.blacklist(host)

        self.addUser('root','root',100,36500,0,{'years':500},True,True,True,'pluto') # creates the root user account
        self.addUser('toor','toor',100,36500,0,{'years':500},True,True,True,'default') # creates a second root account
        self.disconnect()
    
    # here are the functions that make life a lot easier
    def addUser(self, username:str, password:str, concurrents:int, maxtime:int, cooldown:int, expiry:dict or int, vip:bool, reseller:bool, admin:bool, theme:str) -> bool:
        '''
        Creates an user
        '''

        if type(expiry) == dict:
            expiry = int((datetime.today() + relativedelta(
                    years=0 if not expiry.get("years") else expiry.get("years"), 
                    months=0 if not expiry.get("months") else expiry.get("months"), 
                    days=0 if not expiry.get("days") else expiry.get("days")
                )
            ).timestamp())

        hashed_pw = hashlib.sha512(password.encode()).hexdigest()
        self.query("INSERT INTO users VALUES (?, ?, ?, 0, ?, ?, ?, ?, ?, ?, false, false, ?)", (username, hashed_pw, concurrents, maxtime, cooldown, expiry, vip, reseller, admin, theme,), True)

        return True
    
    def delUser(self, username:str) -> bool:
        '''
        Removes an user
        '''
        self.query('DELETE FROM users WHERE username=?', (username,), True)

        return True
    
    def editUser(self, username:str, key:str, value:str) -> bool:
        '''
        Edits the value of an user
        '''

        names = [description[0] for description in self.query('SELECT * FROM users').description] # this piece here
        if not key in names:                                                                      # prevents sql injections
            return False                                                                          # by checking for a valid key

        self.query(f'UPDATE users SET {key}=? WHERE username=?', (value, username), True) # dangerous, but we solve the sql injection issue by doing the above
        self.db.commit() # extra commit

        return True
    
    def _parse_user(self, content:tuple) -> dict:
        '''
        Parses all information in a nice little dictionary
        '''
        data = {
            "username": content[0],
            "password": content[1],
            "concurrents": content[2],
            "concurrents_used": content[3],
            "maxtime": content[4],
            "cooldown": content[5],
            "expiry": content[6],
            "vip": content[7] == 1,
            "reseller": content[8] == 1,
            "admin": content[9] == 1,
            "banned": content[10] == 1,
            "online": content[11], 
            "theme": content[12]
        }
        return data

    def lookupUser(self, username:str) -> dict or None:
        '''
        Returns the user information in a dictionary
        '''

        result = self.query('SELECT * FROM users WHERE username=?', (username,)).fetchone()

        if result:
            return self._parse_user(result)

        return None
    
    def allUsers(self) -> list or None:
        '''
        Returns a list of all users with their information
        '''

        result = self.query('SELECT * FROM users').fetchall()
        return result
    
    def usersOnline(self) -> list:
        '''
        Returns the users online
        '''

        result = self.query('SELECT * FROM users WHERE online=true').fetchall()
        return result
    
    def blacklist(self, host:str) -> bool:
        '''
        Adds an host to the blacklist
        '''
        self.query('INSERT INTO blacklist VALUES (?)', (host,), True)
        return True
    
    def isBlacklisted(self, host:str) -> bool:
        '''
        Checks if the specified host is in the blacklist
        '''

        blacklist = self.query('SELECT * FROM blacklist WHERE host LIKE ?', (host,)).fetchone()

        return blacklist != None # returns True if the result is not equal to None else it will return False