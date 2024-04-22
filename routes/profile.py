from flask import Blueprint, render_template, redirect, request
from db.aclhemy import sql_session, User, Review
from flask_login import current_user
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import os

blueprint = Blueprint(
    'profile',
    __name__,
    template_folder='templates'
)


class ProfileForm(FlaskForm):
    username = StringField('логин')
    description = StringField('описание')
    link = StringField('ссылка')
    submit = SubmitField('сохранить')


@blueprint.route('/profile/<int:user_id>')
def load_profile(user_id):
    """
    Загрузить профиль пользователя с отзывами
    :param user_id: ID пользователя
    :return:
    """
    user = sql_session.query(User).filter(User.id == user_id).first()

    is_author = False
    if current_user.id == user.id:
        is_author = True

    reviews = sql_session.query(Review).filter(Review.creator == user_id).all()

    date = datetime.fromtimestamp(int(float(user.regdate))).strftime('%d.%m.%Y')

    return render_template('profile.html', is_author=is_author, user=user,
                           regdate=date, reviews=reviews, count_reviews=len(reviews))


@blueprint.route('/profile/edit/<int:user_id>', methods=['POST', 'GET'])
def load_edit_profile(user_id):
    """
    Открытие страницы для редактирования профиля. Также создаются формы, обрабатываются, загружается фотография
    :param user_id: ID пользователя
    :return:
    """
    user = sql_session.query(User).filter(User.id == user_id).first()
    form = ProfileForm()

    if current_user.id != user.id:
        return redirect('/profile/' + str(user_id))

    if form.validate_on_submit():
        username = request.form['username']
        description = request.form['description']
        link = request.form['link']

        user = sql_session.query(User).filter(User.username == current_user.username).first()
        exist = sql_session.query(User).filter(User.username == username).first() is not None
        if not exist:
            user.username = username

        user.profile_description = description
        user.link = link
        sql_session.commit()

        return redirect('/profile/' + str(user_id))

    elif request.method == 'POST':
        file = request.files['file']

        if file:
            filename = os.path.join(f'static/img/profile_{current_user.id}.png')
            file.save(filename)

        return redirect('/profile/' + str(user_id))

    return render_template('edit_profile.html', user=user, form=form)
