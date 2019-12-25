# local imports
from app import app

# library imports
from datetime import date
from flask_login import current_user

# function for printing to special usage logs
def ulog(msg):
    fp = open('usage_logs.txt', 'a')
    print('--- ', current_user.username, ' ---- ', date.today(), ' ---', file=fp)
    print(msg, file=fp)
    fp.close()