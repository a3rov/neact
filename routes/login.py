import hashlib

from flask import Blueprint, render_template, redirect, request
from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from db.aclhemy import sql_session, User

blueprint = Blueprint(
    'login',
    __name__,
    template_folder='templates'
)


class LoginForm(FlaskForm):
    username = StringField('логин', validators=[DataRequired()])
    password = PasswordField('пароль', validators=[DataRequired()])
    submit = SubmitField('войти')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        user = sql_session.query(User).filter((User.username == username) | (User.email == username)).first()
        if user is None:
            return render_template('login.html',
                                   message="Такого аккаунта не существует!",
                                   form=form)

        salt_from_storage = user.password[:32]
        key_from_storage = user.password[32:]

        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt_from_storage, 100000)

        if user and key_from_storage == new_key:
            login_user(user, remember=True)
            return redirect("/tasks")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)
