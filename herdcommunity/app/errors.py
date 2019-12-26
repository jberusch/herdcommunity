# local imports
from app import app, db
from app.helpers import ulog

# library imports
from flask import render_template
from flask_login import current_user

@app.errorhandler(404)
def not_found_error(error):
    # ulog('404 -> encounted by {}'.format(current_user))
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    ulog('500 -> encounted by {}'.format(current_user))
    db.session.rollback()
    return render_template('500.html'), 500