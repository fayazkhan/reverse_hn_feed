from flask.ext.script import Manager

from reverse_hn_feed import app, db, sync_with_hacker_news


manager = Manager(app)


@manager.command
def sync():
    sync_with_hacker_news()


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
