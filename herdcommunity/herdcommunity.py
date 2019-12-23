from app import app, db
from app.models import User, Destination, Association

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Destination': Destination, 'Association': Association}