'''
Paralysis C2 source
written by Null
'''

from threading import Lock

class Core:
    isAlive = True # setting this bool to False causes all infinite loops to shut down
    threadLock = Lock() # prevents threads from accessing the same thing at the same time
    defaultConfig = '''''' # default configuration
    motd = 'Thanks for using Paralysis C2' # default motd