from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

# The representation of a many-to-many relationship requires the use of an
# auxiliary table called an association table
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
    )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # backref, let's us access posts from Posts table using
    # user.posts attribute
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
    # In general, you will want to work with UTC dates and times in a server
    # application.
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    # Accounts are active upon creation
    account_active = db.Column(db.Boolean(create_constraint=True), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    primary_contact = db.Column(db.String(120), nullable=False)
    primary_email = db.Column(db.String(120), nullable=False)
    # TODO: figure out how to store phone numbers reliably
    primary_phone = db.Column(db.String(20), nullable=False)
    secondary_contact = db.Column(db.String(120))
    secondary_email = db.Column(db.String(120))
    secondary_phone = db.Column(db.String(20))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'),
                           nullable=False)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    address1 = db.Column(db.String(120), nullable=False)
    address2 = db.Column(db.String(120))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    country = db.Column(db.String(2), nullable=False)
    postal_code = db.Column(db.String(16), nullable=False)


# Because Flask-Login knows nothing about databases,
# it needs the application's help in loading a user.
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
