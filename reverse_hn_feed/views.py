from flask import redirect, request, url_for
from flask_admin import Admin, helpers as admin_helpers
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user, Security, SQLAlchemyUserDatastore
from sqlalchemy import func

from reverse_hn_feed import app, db, Role, User, UserNewsItem


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


app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_URL_PREFIX'] = "/admin"
app.config['SECURITY_LOGIN_URL'] = "/login/"
app.config['SECURITY_LOGOUT_URL'] = "/logout/"
app.config['SECURITY_REGISTER_URL'] = "/register/"
app.config['SECURITY_POST_LOGIN_VIEW'] = "/admin/usernewsitem/"
app.config['SECURITY_POST_LOGOUT_VIEW'] = "/admin/"
app.config['SECURITY_POST_REGISTER_VIEW'] = "/admin/usernewsitem/"
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
admin = Admin(app, base_template='my_master.html', name='reverse_hn_feed')
admin.add_view(UserNewsItemModelView(UserNewsItem, db.session))


@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
    )
