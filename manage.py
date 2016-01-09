from flask.ext.script import Manager
from hackernews import HackerNews

from reverse_hn_feed.app import app, db, NewsItem, User, UserNewsItem


manager = Manager(app)


@manager.command
def sync():
    hn = HackerNews()
    for story_id in hn.top_stories(limit=90):
        story = hn.get_item(story_id)
        persisted_news_item = NewsItem.query.get(story_id)
        if persisted_news_item:
            print "Updating story:", story_id
            persisted_news_item.upvotes = story.score
        else:
            print "Adding story:", story_id
            news_item = NewsItem(
                id=story_id, url=story.url, posted_on=story.submission_time,
                upvotes=story.score)
            db.session.add(news_item)
            for user in User.query.all():
                db.session.add(UserNewsItem(user=user, news_item=news_item))
    db.session.commit()


@manager.command
def create():
    db.create_all()


@manager.command
def run():
    app.run()


@manager.command
def hello():
    print "hello"


if __name__ == "__main__":
    manager.run()
