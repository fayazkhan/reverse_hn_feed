from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import (
    RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin)
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reverse_hn_feed.db'
app.config['SECRET_KEY'] = 'secret key'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_CONFIRMABLE'] = False
db = SQLAlchemy(app)
admin = Admin(app, name='reverse_hn_feed')


class NewsItem(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    url = db.Column(db.String)
    hn_url = db.Column(db.String)
    posted_on = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer)


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    roles = db.relationship(Role, secondary=roles_users)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
admin.add_view(ModelView(NewsItem, db.session))
