from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    handle = db.Column(db.String(32), index=True, unique=True)
    displayed_name = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    status_message = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    profile_pic = db.Column(db.String(128), unique=True)
    last_seen = db.Column(db.DateTime, index=True)
    posts = db.relationship(
        'Post',
        backref='author',
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {user.handle} {user.displayed_name}>"

post_tree = db.Table(
    'post_tree',
    db.Column('parent_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('child_id', db.Integer, db.ForeignKey('post.id'))
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String())
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    edited = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    comments = db.relationship(
        'Post',
        backref=db.backref(
            'comment_to',
            remote_side=id,
        ),
        cascade='delete'
    )

    def __repr__(self):
        return f'<Post {self.user_id}@{self.timestamp}>'
