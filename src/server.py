from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database_create import User, ReviewsData, NeuralAnalysisRequest  # Убедитесь, что модель User импортируется корректно
from dotenv import load_dotenv
import os
import hashlib
from api_get import start_neural_analysis
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

DATABASE_URL = os.getenv("DATABASE_URL")
app = Flask(__name__)
app.debug = True
CORS(app)

# Настройка JWT
app.config['JWT_SECRET_KEY'] = 'ino_pepper_coding'  # Замените на ваш секретный ключ
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(weeks=1)
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
        worker_ids.sort(reverse=True)
        return jsonify(workers_data=worker_ids), 200
    finally:
        session.close()

@app.route('/start_solo_analys', methods=['POST'])
@jwt_required()
def start_analysis():
    data = request.json
    worker_ids = data.get('worker_ids')

    if not worker_ids or not isinstance(worker_ids, list):
        return jsonify({"error": "Некорректные данные. worker_ids должен быть списком"}), 400

    session = Session()
    existing_request = session.query(NeuralAnalysisRequest).filter(
        NeuralAnalysisRequest.worker_ids == worker_ids
    ).first()
    if existing_request:
        session.close()
        return jsonify({
            "request_id": existing_request.id,
            "analysis_result": existing_request.analysis_result,
            "analysis_status": existing_request.analysis_status
        }), 200

    analysis_request = NeuralAnalysisRequest(
        worker_ids=worker_ids,
        analysis_status="in_progress"
    )
    worker_id.append("good")
    worker_id.append("bad")
    session.add(analysis_request)
    session.commit()

    # Получаем ID перед закрытием сессии
    request_id = analysis_request.id
    session.close()

    # Запускаем фоновую задачу анализа
    executor.submit(start_neural_analysis, worker_ids)

    return jsonify({"message": "Анализ начат", "request_id": request_id}), 201

@app.route('/start_analysis', methods=['POST'])
@jwt_required()
def start_analysis():
    data = request.json
    worker_ids = data.get('worker_ids')

    if not worker_ids or not isinstance(worker_ids, list):
        return jsonify({"error": "Некорректные данные. worker_ids должен быть списком"}), 400

    session = Session()
    existing_request = session.query(NeuralAnalysisRequest).filter(
        NeuralAnalysisRequest.worker_ids == worker_ids
    ).first()

    if existing_request:
        session.close()
        return jsonify({
            "request_id": existing_request.id,
            "analysis_result": existing_request.analysis_result,
            "analysis_status": existing_request.analysis_status
        }), 200

    # Создаем новый запрос
    analysis_request = NeuralAnalysisRequest(
        worker_ids=worker_ids,
        analysis_status="in_progress"
    )
    session.add(analysis_request)
    session.commit()

    # Получаем ID перед закрытием сессии
    request_id = analysis_request.id
    session.close()

    # Запускаем фоновую задачу анализа
    executor.submit(start_neural_analysis, worker_ids)

    return jsonify({"message": "Анализ начат", "request_id": request_id}), 201



@app.route('/add_review', methods=['POST'])
@jwt_required()
def add_review():
    data = request.json
    reviewer_id = data.get("reviewer_id")
    worker_id = data.get("worker_id")
    review_text = data.get("review_text")

    if not worker_id or not review_text or not reviewer_id:
        return jsonify({"error": "Поля не заполнены"}), 400

    session = Session()
    # try:
    # Создаем новый отзыв
    new_review = ReviewsData(ID_reviewer=reviewer_id, ID_under_review=worker_id, review=review_text)

    session.add(new_review)
    session.commit()

    return jsonify({"message": "Отзыв успешно добавлен", "ID_under_review": worker_id}), 201
    # except Exception as e:
        # session.rollback()
        # return jsonify({"error": str(e)}), 500
    # finally:
    session.close()


@app.route('/get_all_analysis_requests', methods=['GET'])
# @jwt_required()
def get_all_analysis_requests():
    session = Session()
    try:
        analysis_requests = session.query(NeuralAnalysisRequest).all()

        response_data = [
            {
                "id": request.id,
                "worker_ids": request.worker_ids,
                "analysis_status": request.analysis_status,
                "analysis_result": request.analysis_result
            }
            for request in analysis_requests
        ]

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
