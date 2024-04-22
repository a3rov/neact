from flask_restful import Resource
from flask import jsonify
from db.aclhemy import sql_session, Task


class TaskResource(Resource):
    def get(self, task_id):
        task = sql_session.query(Task).get(task_id)
        if task is None:
            return jsonify({'task': 'Не существует'})

        return jsonify(
            {'task': {point: arg for (point, arg) in task.__dict__.items() if point != '_sa_instance_state'}})


class TaskListResource(Resource):
    def get(self):
        tasks = sql_session.query(Task).all()
        return jsonify({task.id: {point: arg for (point, arg) in task.__dict__.items()
                                  if point != '_sa_instance_state'} for task in tasks})
