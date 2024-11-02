from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем запросы с любых доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Пример данных для демонстрации
workers_data = {
    "worker_ids": ["worker_1", "worker_2", "worker_3", "worker_4"],
}

reviews_data = {
    "worker_1": "Отличный работник, быстро выполняет задачи.",
    "worker_2": "Умеет работать в команде, отзывчивый.",
    "worker_3": "Не всегда соблюдает сроки, но хорошо разбирается в вопросах.",
    "worker_4": "Требует дополнительного обучения, но проявляет интерес."
}

# Модель для запроса на получение отзывов
class ReviewRequest(BaseModel):
    worker_ids: List[str]

# Модель для формата ответа на отзыв
class ReviewResponse(BaseModel):
    worker_id: str
    user_feedback: str

@app.get("/get_all")
async def get_all_workers():
    return workers_data

@app.post("/get_review_selected")
async def get_review_selected(request: ReviewRequest):
    responses = []
    for worker_id in request.worker_ids:
        if worker_id in reviews_data:
            responses.append(ReviewResponse(worker_id=worker_id, user_feedback=reviews_data[worker_id]))
        else:
            responses.append(ReviewResponse(worker_id=worker_id, user_feedback="Генерирую сводку"))
    return responses



# Запуск приложения можно сделать через команду:
# uvicorn имя_файла:app --reload
