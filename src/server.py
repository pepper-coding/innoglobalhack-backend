from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database_create import User, ReviewsData  # Убедитесь, что модель User импортируется корректно
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
        if user and user.password == hashlib.sha256(password.encode()).hexdigest():
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
    session = Session()
    try:
        # Получаем уникальные ID_under_review из таблицы reviews_data
        unique_worker_ids = session.query(ReviewsData.ID_under_review).distinct().all()
        # Преобразуем результаты в плоский список
        worker_ids = [worker_id[0] for worker_id in unique_worker_ids]

        return jsonify(workers_data=worker_ids), 200
    finally:
        session.close()

@app.route('/get_summary_selected', methods=['POST'])
@jwt_required()
def get_summary_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    session = Session()
    try:
        for worker_id in worker_ids:
            # Получаем сводку из таблицы summary_data
            summary = session.query(SummaryData).filter(SummaryData.ID_under_review == worker_id).first()
            if summary:
                responses.append({"worker_id": worker_id, "user_summary": summary.summary_review})
            else:
                responses.append({"worker_id": worker_id, "user_summary": "Генерирую сводку"})
        return jsonify(responses), 200
    finally:
        session.close()


@app.route('/get_review_selected', methods=['POST'])
@jwt_required()
def get_review_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    session = Session()
    try:
        for worker_id in worker_ids:
            # Получаем отзывы из таблицы reviews_data
            reviews = session.query(ReviewsData).filter(ReviewsData.ID_under_review == worker_id).all()
            user_feedback = [review.review for review in reviews]
            responses.append({"worker_id": worker_id, "user_feedback": user_feedback})
        return jsonify(responses), 200
    finally:
        session.close()

# Запуск приложения
if __name__ == '__main__':
    print(DATABASE_URL)
    app.run(host="0.0.0.0", port=8000)
