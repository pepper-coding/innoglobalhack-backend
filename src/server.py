from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware
from config import DATABASE_URL
from database_create import User, ReviewsData, NeuralAnalysisRequest  # Убедитесь, что модель User импортируется корректно
from dotenv import load_dotenv
from api_get import start_neural_analysis
import os
import hashlib
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import List

load_dotenv()

executor = ThreadPoolExecutor(max_workers=5)

DATABASE_URL = os.getenv("DATABASE_URL")
app = FastAPI(
    title="Hr Helper",  # Укажите нужное название
    description="Помощник по генерации сводок о работе персонала",  # Укажите описание
    version="1.0.0",
     openapi_tags=[
        {
            "name": "API pepper_coding",
            "description": "Реализованные запросы"
        }
    ]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Настройка JWT
class Settings(BaseModel):
    authjwt_secret_key: str = "ino_pepper_coding"
    authjwt_access_token_expires: timedelta = timedelta(weeks=1)

@AuthJWT.load_config
def get_config():
    return Settings()

# Создание сессии базы данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Зависимость для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модель для авторизации
class LoginModel(BaseModel):
    login: str
    password: str

# Модель для создания анализа
class AnalysisRequestModel(BaseModel):
    worker_ids: List[int]

# Модель для добавления отзыва
class ReviewModel(BaseModel):
    reviewer_id: float
    worker_id: float
    review_text: str

@app.post('/login', tags=["API pepper_coding"])
def login(data: LoginModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    user = db.query(User).filter(User.login == data.login).first()

    if not user or user.password != hashlib.sha256(data.password.encode()).hexdigest():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")

    access_token = Authorize.create_access_token(subject=user.id)
    return JSONResponse({"access_token": access_token})

@app.get('/get_all', tags=["API pepper_coding"])
def get_all_workers(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    unique_worker_ids = db.query(ReviewsData.ID_under_review).distinct().all()
    worker_ids = sorted([worker_id[0] for worker_id in unique_worker_ids], reverse=True)
    worker_ids.remove(-1)
    worker_ids.remove(-2)
    return JSONResponse({"workers_data": worker_ids})

@app.post('/start_solo_analys', tags=["API pepper_coding"])
def start_solo_analys(data: AnalysisRequestModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    existing_request = db.query(NeuralAnalysisRequest).filter(NeuralAnalysisRequest.worker_ids == data.worker_ids).first()
    if existing_request:
        return JSONResponse({
            "request_id": existing_request.id,
            "analysis_result": existing_request.analysis_result,
            "analysis_status": existing_request.analysis_status
        })

    analysis_request = NeuralAnalysisRequest(worker_ids=data.worker_ids, analysis_status="in_progress")
    db.add(analysis_request)
    db.commit()
    request_id = analysis_request.id

    executor.submit(start_neural_analysis, data.worker_ids)
    return JSONResponse({"message": "Анализ начат", "request_id": request_id})


@app.get("/docs", include_in_schema=False)
def get_docs():
    return {"message": "Swagger documentation is available at /docs"}


@app.post('/start_analysis', tags=["API pepper_coding"])
def start_analysis(data: AnalysisRequestModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    existing_request = db.query(NeuralAnalysisRequest).filter(NeuralAnalysisRequest.worker_ids == data.worker_ids).first()
    if existing_request:
        return JSONResponse({
            "request_id": existing_request.id,
            "analysis_result": existing_request.analysis_result,
            "analysis_status": existing_request.analysis_status
        })

    analysis_request = NeuralAnalysisRequest(worker_ids=data.worker_ids, analysis_status="in_progress")
    db.add(analysis_request)
    db.commit()
    request_id = analysis_request.id

    executor.submit(start_neural_analysis, data.worker_ids)
    return JSONResponse({"message": "Анализ начат", "request_id": request_id})

@app.post('/add_review', tags=["API pepper_coding"])
def add_review(data: ReviewModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    new_review = ReviewsData(ID_reviewer=data.reviewer_id, ID_under_review=data.worker_id, review=data.review_text)
    db.add(new_review)
    db.commit()

    return JSONResponse({"message": "Отзыв успешно добавлен", "ID_under_review": data.worker_id})

class ReviewSchema(BaseModel):
    ID_reviewer: str
    ID_under_review: str
    review: str

@app.post('/add_json_reviews', tags=["API pepper_coding"])
def add_reviews(reviews: List[ReviewSchema], db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    for review_data in reviews:
        new_review = ReviewsData(
            ID_reviewer=review_data.ID_reviewer,
            ID_under_review=review_data.ID_under_review,
            review=review_data.review
        )
        db.add(new_review)

    db.commit()
    return JSONResponse({"message": "Отзывы успешно добавлены"})



@app.get('/get_all_analysis_requests', tags=["API pepper_coding"])
def get_all_analysis_requests(db: Session = Depends(get_db)):
    analysis_requests = db.query(NeuralAnalysisRequest).all()

    response_data = []
    total_average = 0
    count = 0

    for request in analysis_requests:
        # Предполагается, что analysis_result - это двумерный список строк
        # Преобразуем строки в числовые значения
        numbers = []
        if isinstance(request.analysis_result, list):
            for inner_list in request.analysis_result:
                for item in inner_list:
                    # Предполагается, что item - это строка, которая может содержать цифры
                    digits = ''.join(filter(str.isdigit, item))  # Извлекаем только цифры
                    if digits:  # Проверяем, не пустая ли строка
                        numbers.append(int(digits))

        if numbers:  # Если нашли числа, считаем среднее
            average = sum(numbers) / len(numbers)
            total_average += average
            count += 1  # Увеличиваем счетчик для средних значений

            response_data.append({
                "id": request.id,
                "worker_ids": request.worker_ids,
                "analysis_status": request.analysis_status,
                "analysis_result": request.analysis_result,
                "average": average  # Добавляем среднее значение в ответ
            })
        else:
            response_data.append({
                "id": request.id,
                "worker_ids": request.worker_ids,
                "analysis_status": request.analysis_status,
                "analysis_result": request.analysis_result,
                "average": None  # Если нет чисел, возвращаем None
            })

    # Рассчитываем общее среднее значение, если есть хоть одно среднее
    average_rating = total_average / count if count > 0 else None

    response = JSONResponse(content=response_data)
    response.headers['average_rating'] = str(average_rating) if average_rating is not None else 'N/A'  # Устанавливаем заголовок

    return response

@app.post('/get_analysis_results', tags=["API pepper_coding"])
def get_analysis_results(data: AnalysisRequestModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    results = db.query(NeuralAnalysisRequest).filter(
        func.cardinality(NeuralAnalysisRequest.worker_ids) == 1
    ).all()

    if not data.worker_ids or len(data.worker_ids) != 1:
        return JSONResponse({"message": "worker_ids должен содержать ровно одно значение"}, status_code=400)

    worker_id_to_check = str(data.worker_ids[0]).strip()  # Удаляем пробелы
    filtered_results = []
    for result in results:
        if worker_id_to_check in result.worker_ids:
            filtered_results.append(result)


    if not filtered_results:
        return JSONResponse({"message": "Запрос не найден, запросите сводку"}, status_code=404)

    response = []
    for result in filtered_results:
        criteria_scores = {}
        for analysis_text in result.analysis_result:
            criteria_scores.update(parse_analysis_result(analysis_text))

        response.append({
            "criteria_scores": criteria_scores
        })

    return JSONResponse(response)

def parse_analysis_result(analysis_result_text: str):
    criteria_scores = {}
    # Разбиваем текст по строкам
    lines = analysis_result_text.split('\n\n')

    for line in lines:
        if ':' in line:  # Убедимся, что строка содержит критерий
            criterion, score = line.split(':', 1)
            criterion = criterion.strip()  # Удаляем пробелы в начале и конце критерия

            # Извлекаем только целочисленное значение из оценки
            score_value = ''.join(filter(str.isdigit, score))  # Оставляем только цифры
            if score_value:  # Проверяем, что есть хотя бы одна цифра

                criteria_scores[criterion] = int(score_value[0])  # Конвертируем в целое число

    return criteria_scores



class WorkerIdsModel(BaseModel):
    worker_ids: List[int]
@app.post('/get_review_selected', tags=["API pepper_coding"])
def get_review_selected(data: WorkerIdsModel, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    responses = []
    for worker_id in data.worker_ids:
        reviews = db.query(ReviewsData).filter(ReviewsData.ID_under_review == worker_id).all()
        user_feedback = [review.review for review in reviews]
        responses.append({"worker_id": worker_id, "user_feedback": user_feedback})
    return JSONResponse(responses)
