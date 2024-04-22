from flask import Blueprint, render_template
from flask_login import AnonymousUserMixin
from flask_login import current_user

blueprint = Blueprint(
    'page_index',
    __name__,
    template_folder='templates'
)


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


@blueprint.route('/')
@blueprint.route('/index')
def load_page():
    """
    Загрузка основной страницы
    :return:
    """

    text = 'войти'
    link = 'login'

    try:
        text = current_user.username
        link = 'tasks'
    except:
        pass

    return render_template('index.html', link=link, text=text)
