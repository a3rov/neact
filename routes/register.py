from flask import Blueprint, render_template, redirect, request
from db.aclhemy import sql_session, User

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

import hashlib
from data.salt import salt

from datetime import datetime
from time import mktime as create_unix_time


blueprint = Blueprint(
    'register',
    __name__,
    template_folder='templates'
)


class RegisterForm(FlaskForm):
    email = StringField('e-mail', validators=[DataRequired()])
    username = StringField('логин', validators=[DataRequired()])
    password = PasswordField('пароль', validators=[DataRequired()])
    submit = SubmitField('зарегистрироваться')


def return_with_message(form, text):
    return render_template('register.html', title='Регистрация', form=form, message=text)


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
    
        user = sql_session.query(User).filter((User.username == username) | (User.email == email)).first()
        if user is not None:
            if user.username == username:
                return return_with_message(form, 'Аккаунт с таким логином уже существует')
            
            if user.email == email:
                return return_with_message(form, 'Аккаунт с такой почтой уже существует')
        
        else:
            if len(email) > 360:
                return return_with_message(form, 'Длина почты не должна превышать 360 символов!')

            if len(username) > 32:
                return return_with_message(form, 'Длина логина не должна превышать 32 символа!')

            if len(password) > 64:
                return return_with_message(form, 'Длина пароля не должна не превышать 64 символа!')
            
            key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            storage = salt + key 

            user = User()
            user.email = email
            user.username = username
            user.password = storage
            user.regdate = create_unix_time(datetime.now().date().timetuple())
            user.link_type = 'Telegram'
            user.link = 't.me'
            sql_session.add(user)
            sql_session.commit()

            return redirect('/login')

    return render_template('register.html', title='Регистрация', form=form)
