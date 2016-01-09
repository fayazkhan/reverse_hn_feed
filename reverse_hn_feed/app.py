from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import UserMixin, Security, SQLAlchemyUserDataStore
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reverse_hn_feed.db'
app.config['SECRET_KEY'] = 'secret key'
db = SQLAlchemy(app)
admin = Admin(app, name='reverse_hn_feed')


class NewsItem(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    url = db.Column(db.String)
    hn_url = db.Column(db.String)
    posted_on = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer)


class User(db.Model, UserMixin):

    user_name = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)


user_datastore = SQLAlchemyUserDataStore(db, User)
security = Security(app, user_datastore)
admin.add_view(ModelView(NewsItem, db.session))

if __name__ == '__main__':
    app.run(debug=True)
