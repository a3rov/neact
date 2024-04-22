from flask import Flask, redirect
from routes import index, login, register, tasks, profile
from api import tasks_resources
from flask_login import LoginManager, login_required, logout_user
from db.aclhemy import sql_session, User
from flask_restful import reqparse, abort, Api
import datetime


app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

api = Api(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return sql_session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


app.config['SECRET_KEY'] = 'neact.secretkey.value82i2sdAJdlkOsd209eaSaSUIOQ2sYQ-SQWUESQ-EQeosdpqSaSAEYAGDADSasZcdlkzc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'


if __name__ == '__main__':
    app.register_blueprint(index.blueprint)
    app.register_blueprint(register.blueprint)
    app.register_blueprint(login.blueprint)
    app.register_blueprint(tasks.blueprint)
    app.register_blueprint(profile.blueprint)

    api.add_resource(tasks_resources.TaskListResource, '/api/tasks')
    api.add_resource(tasks_resources.TaskResource, '/api/tasks/<int:task_id>')

    app.run(host='127.0.0.1', port=80)
