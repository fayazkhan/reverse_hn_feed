import json

from flask import Flask, redirect, request, url_for
from flask_admin import Admin, helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_security import (
    current_user, RoleMixin, Security, SQLAlchemyUserDatastore, UserMixin)
from flask_sqlalchemy import SQLAlchemy
from hackernews import HackerNews
from sqlalchemy import func


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
admin = Admin(app, base_template='my_master.html', name='reverse_hn_feed')


class NewsItem(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    url = db.Column(db.String)
    hn_url = db.Column(db.String)
    posted_on = db.Column(db.DateTime)
    upvotes = db.Column(db.Integer)
    comments = db.Column(db.Integer)


roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    active = db.Column(db.Boolean)
    roles = db.relationship(Role, secondary=roles_users)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        for news_item in NewsItem.query.all():
            db.session.add(UserNewsItem(user=self, news_item=news_item))


class UserNewsItem(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)
    news_id = db.Column(db.Integer, db.ForeignKey(NewsItem.id))
    news_item = db.relationship(NewsItem)
    unread = db.Column(db.Boolean, default=False)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route('/')
def index():
    return redirect(url_for('admin.index'))


class UserNewsItemModelView(ModelView):

    can_create = False
    can_edit = False
    column_list = ('news_item.url', 'news_item.hn_url', 'news_item.posted_on',
                   'news_item.upvotes', 'news_item.comments', 'unread')
    column_editable_list = ('unread',)
    column_sortable_list = ('news_item.posted_on',)
    column_default_sort = ('news_item.posted_on', True)

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible() and not current_user.is_authenticated:
            return redirect(url_for('security.login', next=request.url))

    def get_query(self):
        return self.session.query(UserNewsItem).filter(
            UserNewsItem.user_id == current_user.id)

    def get_count_query(self):
        return self.session.query(func.count('*')).filter(
            UserNewsItem.user_id == current_user.id)


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )


admin.add_view(UserNewsItemModelView(UserNewsItem, db.session))


def sync_with_hacker_news():
    hn = HackerNews()
    for story_id in hn.top_stories(limit=90):
        story = hn.get_item(story_id)
        persisted_news_item = NewsItem.query.get(story_id)
        if persisted_news_item:
            print "Updating story:", story_id
            persisted_news_item.upvotes = story.score
            persisted_news_item.comments = comment_count(story)
        else:
            print "Adding story:", story_id
            news_item = NewsItem(
                id=story_id, url=story.url, posted_on=story.submission_time,
                upvotes=story.score,
                comments=comment_count(story))
            db.session.add(news_item)
            for user in User.query.all():
                db.session.add(UserNewsItem(user=user, news_item=news_item))
    db.session.commit()


def comment_count(story):
    return json.loads(story.raw).get('descendants', 0)
