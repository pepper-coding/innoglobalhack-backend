from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database_create import User  # Убедитесь, что модель User импортируется корректно
from dotenv import load_dotenv
import os
import hashlib
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
app.debug = True
CORS(app)

# Настройка JWT
app.config['JWT_SECRET_KEY'] = 'ino_pepper_coding'  # Замените на ваш секретный ключ
jwt = JWTManager(app)

# Создание сессии базы данных
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Пример данных для демонстрации
workers_data = {
    "worker_ids": ["worker_1", "worker_2", "worker_3", "worker_4"],
}

summary_data = {
    "worker_1": "Отличный работник, быстро выполняет задачи.",
    "worker_2": "Умеет работать в команде, отзывчивый.",
    "worker_3": "Не всегда соблюдает сроки, но хорошо разбирается в вопросах.",
    "worker_4": "Требует дополнительного обучения, но проявляет интерес."
}

reviews_data = {
    "worker_1": {"Отличный работник, быстро выполняет задачи.", "Бла бла 1", "Бла бла 2"},
    "worker_2": {"Умеет работать в команде, отзывчивый.", "Бла бла 1", "Бла бла 2"},
    "worker_3": {"Не всегда соблюдает сроки, но хорошо разбирается в вопросах.", "Бла бла 1", "Бла бла 2"},
    "worker_4": {"Требует дополнительного обучения, но проявляет интерес.", "Бла бла 1", "Бла бла 2"},
}

@app.route('/login', methods=['POST'])
def login():
    # Получаем логин и пароль из запроса
    login = request.json.get('login')
    password = request.json.get('password')

    # Создаем сессию для работы с базой данных
    session = Session()

    try:
        # Находим пользователя по логину
        user = session.query(User).filter(User.login == login).first()

        # Проверяем, существует ли пользователь и совпадают ли пароли
        if user and user.password == password:
            # Создаем токен доступа
            token = create_access_token(identity=user.id)
            return jsonify(access_token=token), 200
        else:
            return jsonify(msg="Неверный логин или пароль"), 401  # Возвращаем ошибку при неверном логине или пароле
    finally:
        session.close()  # Закрываем сессию после завершения работы


@app.route('/get_all', methods=['GET'])
@jwt_required()
def get_all_workers():
    return jsonify(workers_data)

@app.route('/get_summary_selected', methods=['POST'])
@jwt_required()
def get_summary_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    for worker_id in worker_ids:
        if worker_id in summary_data:
            responses.append({"worker_id": worker_id, "user_summary": summary_data[worker_id]})
        else:
            responses.append({"worker_id": worker_id, "user_summary": "Генерирую сводку"})
    print(responses)
    return jsonify(responses)

@app.route('/get_review_selected', methods=['POST'])
@jwt_required()
def get_review_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    for worker_id in worker_ids:
        if worker_id in reviews_data:
            user_feedback = list(reviews_data[worker_id])
            responses.append({"worker_id": worker_id, "user_feedback": user_feedback})
        else:
            responses.append({"worker_id": worker_id, "user_feedback": "Генерирую сводку"})
    return jsonify(responses)

# Запуск приложения
if __name__ == '__main__':
    print(DATABASE_URL)
    app.run(host="0.0.0.0", port=8000)
