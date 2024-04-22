from flask_restful import Resource
from flask import jsonify
from db.aclhemy import sql_session, Task


class TaskResource(Resource):
    """
    Класс для работы с RESTful-API (одним таском)
    """
    def get(self, task_id):
        """
        Функция для получения json одного Таска
        :param task_id:
        :return:
        """
        task = sql_session.query(Task).get(task_id)
        if task is None:
            return jsonify({'task': 'Не существует'})

        return jsonify(
            {'task': {point: arg for (point, arg) in task.__dict__.items() if point != '_sa_instance_state'}})


class TaskListResource(Resource):
    """
    Класс для работы с RESTful-API (всех тасков)
    """
    def get(self):
        """
        Функция для получения всех Тасков
        :return:
        """
        tasks = sql_session.query(Task).all()
        return jsonify({task.id: {point: arg for (point, arg) in task.__dict__.items()
                                  if point != '_sa_instance_state'} for task in tasks})
