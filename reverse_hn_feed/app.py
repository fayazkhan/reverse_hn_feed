from flask import Flask, redirect, render_template, request, url_for
from flask_admin import Admin, helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_security import (
    current_user, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin)
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
app.config['SECURITY_POST_LOGIN_VIEW'] = "/admin/"
app.config['SECURITY_POST_LOGOUT_VIEW'] = "/admin/"
app.config['SECURITY_POST_REGISTER_VIEW'] = "/admin/"
db = SQLAlchemy(app)
admin = Admin(app, base_template='my_master.html', name='reverse_hn_feed')


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


class UserNewsItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    news_id = db.Column(db.Integer, db.ForeignKey(NewsItem.id))
    unread = db.Column(db.Boolean, default=False)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return render_template('index.html')


class MyModelView(ModelView):

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible() and not current_user.is_authenticated:
            return redirect(url_for('security.login', next=request.url))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


admin.add_view(MyModelView(UserNewsItem, db.session))
