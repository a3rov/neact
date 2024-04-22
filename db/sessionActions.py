from datetime import datetime
from time import mktime as create_unix_time

from db.aclhemy import sql_session, Message


def get_messages(byid: int, toid: int, count: int = 50) -> list:
    """
    Получение диалога с count сообщений с авторами сообщений byid и toid

    :param byid: ID отправителя сообщения
    :param toid: ID получателя сообщения
    :param count: Количество сообщений (по умолчанию 50)
    :return: list с сообщениями
    """
    messages_1 = list(sql_session.query(Message).filter((Message.author == byid),
                                                        (Message.receiver == toid)).limit(count).all()[::-1])
    messages_2 = list(sql_session.query(Message).filter((Message.author == toid),
                                                        (Message.receiver == byid)).limit(count).all()[::-1])

    messages_unix = []
    for message in messages_1:
        messages_unix.append(
            [message.author == byid, message.text, message.date])

    for message in messages_2:
        messages_unix.append(
            [message.author == byid, message.text, message.date])

    messages_unix = sorted(messages_unix, key=lambda x: x[2])

    messages = []
    for message in messages_unix:
        date = datetime.fromtimestamp(int(float(message[2]))).strftime('%H:%M %d.%m')
        messages.append((message[0], message[1], date))

    return messages


def send_message(byid: int, toid: int, text: str):
    """
    Отправка сообщения от byid к toid с текстом text

    :param byid: ID отправителя сообщения
    :param toid: ID получателя сообщения
    :param text: Текст сообщения
    :return:
    """
    message: Message = Message()
    message.author = byid
    message.receiver = toid
    message.text = text
    message.date = create_unix_time(datetime.now().timetuple())
    sql_session.add(message)
    sql_session.commit()
