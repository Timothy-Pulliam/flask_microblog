from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

# The representation of a many-to-many relationship requires the use of an
# auxiliary table called an association table
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # The User class has a new posts field, that is initialized with db.relationship.
    # This is not an actual database field, but a high-level view of the relationship
    # between users and posts, and for that reason it isn't in the database diagram.
    # For a one-to-many relationship, a db.relationship field is normally defined
    # on the "one" side, and is used as a convenient way to get access to the "many".
    # So for example, if I have a user stored in u, the expression u.posts will run a
    # database query that returns all the posts written by that user. The first
    # argument to db.relationship is the model class that represents the "many"
    # side of the relationship. This argument can be provided as a string with
    # the class name if the model is defined later in the module. The backref
    # argument defines the name of a field that will be added to the objects of
    # the "many" class that points back at the "one" object. This will add a
    # post.author expression that will return the user given a post.

    # lazy = true (return a query object so further queries can be made)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    # as a convention let's say that for a pair of users linked by
    # this relationship, the left side user is following the right
    # side user.
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        # because the MD5 support in Python works on bytes
        # and not on strings, I encode the string as bytes
        # before passing it on to the hash function.
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Post.timestamp.desc())

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    # In general, you will want to work with UTC dates and times in a server application.
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


# Because Flask-Login knows nothing about databases,
# it needs the application's help in loading a user.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
