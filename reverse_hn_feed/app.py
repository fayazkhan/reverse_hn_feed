from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reverse_hn_feed.db'
app.config['SECRET_KEY'] = 'secret key'
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_URL_PREFIX'] = "/admin"
app.config['SECURITY_LOGIN_URL'] = "/login/"
app.config['SECURITY_LOGOUT_URL'] = "/logout/"
app.config['SECURITY_REGISTER_URL'] = "/register/"
app.config['SECURITY_POST_LOGIN_VIEW'] = "/admin/usernewsitem/"
app.config['SECURITY_POST_LOGOUT_VIEW'] = "/admin/"
app.config['SECURITY_POST_REGISTER_VIEW'] = "/admin/usernewsitem/"
db = SQLAlchemy(app)
