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

def delete_log(destination_id):
    fp = open('destinations_to_delete.txt', 'a')
    print('User ', current_user.username, 'sent signal to remove destination with id: ', destination_id, file=fp)
    fp.close()