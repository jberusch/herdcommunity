# local imports
from app import db, login

# library imports
from flask_login import UserMixin

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

friendship_identifier = db.Table('friendship_identifier',
    db.Column('user_id', db.Integer, db.ForeignKey('users.user_id')), 
    db.Column('friend_id', db.Integer, db.ForeignKey('users.user_id')),
    db.UniqueConstraint('user_id', 'friend_id', name='unique_friendships')
)

class Association(db.Model):
    __tablename__ = 'associations'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.destination_id'), primary_key=True)
    num_visits = db.Column(db.Integer)
    user = db.relationship("User", back_populates="destinations")
    destination = db.relationship("Destination", back_populates="users")

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), index=True, unique=True)
    destinations = db.relationship('Association', back_populates='user')
    friends = db.relationship('User',
        secondary=friendship_identifier,
        primaryjoin= user_id == friendship_identifier.c.user_id,
        secondaryjoin= user_id == friendship_identifier.c.friend_id)

    def get_id(self):
        return self.user_id

    def add_friend(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)
            friend.friends.append(self)

    def remove_friend(self, friend):
        if friend in self.friends:
            self.friends.remove(friend)
            friend.friends.remove(self)

    def __repr__(self):
        return '<User {}>'.format(self.name)

class Destination(db.Model):
    __tablename__ = 'destinations'
    destination_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    img_src = db.Column(db.String(1000))
    region = db.Column(db.String(50))
    yelp_link = db.Column(db.String(150))
    address = db.Column(db.String(200))
    num_visits = db.Column(db.Integer)
    users = db.relationship('Association', back_populates='destination')

    def get_id(self):
        return self.destination_id

    def __repr__(self):
        return '<Destination {}>'.format(self.name)