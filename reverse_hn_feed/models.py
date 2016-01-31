import json

from flask_security import RoleMixin, UserMixin
from hackernews import HackerNews

from reverse_hn_feed import db


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
