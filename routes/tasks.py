from datetime import datetime
from random import choice

from flask import Blueprint, render_template, redirect, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from db.aclhemy import sql_session, Task, Feedback, User, Review
from db.sessionActions import get_messages, send_message

blueprint = Blueprint(
    'tasks',
    __name__,
    template_folder='templates'
)


class CreateTaskForm(FlaskForm):
    title = StringField('Заголовок задания', validators=[DataRequired()])
    description = StringField('Теперь поподробнее о заказе..', validators=[DataRequired()])
    price = StringField('Оплата', validators=[DataRequired()])
    submit = SubmitField('публикация')


@blueprint.route('/tasks')
def load_tasks():
    if not current_user.is_authenticated:
        return redirect('/login')

    tasks = sql_session.query(Task).filter((Task.status == 'finding') | (Task.author == current_user.id) |
                                           (Task.creator == current_user.id)).all()

    return render_template('tasks.html', current_user=current_user, tasks=tasks)


@blueprint.route('/tasks/<int:task_id>', methods=['GET', 'POST'])
def load_task(task_id):
    """
    В функции мы обрабатываем работу создателя Таска и пользователя, желающего его выполнить

    Если это автор, то ему отображаются FeedBacks (т.е. отклики на исполнение задания) и возможности удалить
    задание, если выбран исполнитель задания, то возможность отказаться, подтвердить успешное выполнение

    Если же это не автор Таска, то пользователю дается возможность оставить отклик, далее, если отклик принят,
    то доступен чат с автором

    :param task_id: получаем ID таска, с которым предстоит работать
    :return: # возвращаем ответ сайта
    """

    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()
    date = task.date
    is_author = current_user.id == task.author
    author = sql_session.query(User).filter(User.id == task.author).first()

    if 'send_message' in request.form.keys():
        text = request.form['input_message_text']
        if not is_author:
            send_message(current_user.id, task.author, text)
        else:
            send_message(current_user.id, task.creator, text)

        return redirect(f'/tasks/{task_id}')

    if not is_author and 'taketask' in request.form.keys():
        if task.status != 'finding':
            return redirect('/tasks')

        feedback = Feedback()
        feedback.task_id = task.id
        feedback.author = current_user.id
        sql_session.add(feedback)
        sql_session.commit()

        return redirect(f'/tasks/{task_id }')

    elif is_author and task.status in 'finding':
        feedbacks = sql_session.query(Feedback).filter(Feedback.task_id == task_id).all()

        feedbacks_for_task_author = []

        for feedback in feedbacks:
            user = sql_session.query(User).filter(User.id == feedback.author).first()
            feedbacks_for_task_author.append([user.id, user.username])

        return render_template('task.html', current_user=current_user, task=task,
                               feedbacks=feedbacks_for_task_author, date_ago=date, author=author)

    elif is_author and task.status in 'closed':
        review = sql_session.query(Review).filter(Review.task_id == task_id).first()

        return render_template('task.html', current_user=current_user, task=task,
                               date_ago=date, review=review, author=author)

    elif is_author and task.status == 'creating':

        person = sql_session.query(User).get(task.creator)
        messages = get_messages(current_user.id, task.creator)
        return render_template('task.html', current_user=current_user, task=task,
                               messages=messages, person=person.username, date_ago=date, author=author)

    elif not is_author and task.status == 'creating':

        person = sql_session.query(User).get(task.author)
        messages = get_messages(current_user.id, task.author)
        return render_template('task.html', current_user=current_user, task=task,
                               messages=messages, person=person.username, date_ago=date, author=author)

    return render_template('task.html', current_user=current_user, task=task, date_ago=date,
                           author=author)


@blueprint.route('/tasks/add', methods=['GET', 'POST'])
def create_task():
    if not current_user.is_authenticated:
        return redirect('/login')

    form = CreateTaskForm()
    if form.validate_on_submit():
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')

        task = Task()
        task.title = title
        task.unique = ''.join([choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
                                       'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                                       'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z',
                                       'x', 'c', 'v', 'b', 'n', 'm', 'Q', 'W', 'E', 'R',
                                       'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F',
                                       'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M']) for _ in range(10)])
        task.description = description
        task.price = price
        task.date = datetime.now().strftime('%H:%M %d.%m.%Y')
        task.author = current_user.id
        task.author_username = current_user.username
        task.status = 'finding'
        sql_session.add(task)
        sql_session.commit()
        return redirect('/tasks')

    return render_template('create_task.html', current_user=current_user, form=form)


@blueprint.route('/tasks/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()

    feedbacks = sql_session.query(Feedback).filter(Feedback.task_id == task_id).all()

    for feedback in feedbacks:
        sql_session.delete(feedback)

    sql_session.commit()

    sql_session.delete(task)
    sql_session.commit()

    return redirect('/tasks')


@blueprint.route('/tasks/set_creator/<int:task_id>/<int:creator_id>', methods=['POST'])
def set_creator(task_id, creator_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()
    task.status = 'creating'
    task.creator = creator_id
    sql_session.commit()

    return redirect(f'/tasks/{task_id}')


@blueprint.route('/tasks/refuse_task/<int:task_id>', methods=['POST'])
@blueprint.route('/tasks/change_creator/<int:task_id>', methods=['POST'])
def remove_creator(task_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()
    task.status = 'finding'
    task.creator = ''
    sql_session.commit()

    return redirect(f'/tasks/{task_id}')


@blueprint.route('/tasks/approve_task/<int:task_id>', methods=['POST'])
def approve_task(task_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()
    task.status = 'closed'
    task.creator = ''
    sql_session.commit()

    return redirect(f'/tasks/{task_id}')


@blueprint.route('/tasks/edit_review/<int:task_id>', methods=['POST'])
def edit_review(task_id):
    if not current_user.is_authenticated:
        return redirect('/login')

    task = sql_session.query(Task).filter(Task.id == task_id).first()
    review = sql_session.query(Review).filter(Review.task_id == task_id).first()
    form_data = request.form
    text = form_data['input_message_text']
    rate = form_data['rating']

    if review is None:

        review = Review()
        review.task_id = task_id
        review.creator = task.creator
        review.author = current_user.id
        review.username = current_user.username

        sql_session.add(review)

    review.rate = rate
    review.text = text

    sql_session.commit()

    return redirect(f'/tasks/{task_id}')
