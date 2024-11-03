import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Float, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
import json
from dataset_format import format_dataset
# Загрузка переменных из .env файла
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# Создание движка базы данных
engine = create_engine(DATABASE_URL)

# Создание базового класса для объявлений моделей
Base = declarative_base()

perfect_and_bad_data = [
    # Отзывы для сотрудника с ID 101 (хорошая производительность)
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Великолепное выполнение всех задач вовремя."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Обладает превосходными навыками командной работы."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Постоянно стремится к улучшению результатов."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Ответственен и способен решать сложные задачи самостоятельно."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Постоянно проявляет инициативу и предлагает новые идеи."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Демонстрирует высокий уровень профессионализма и знаний."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Активно поддерживает своих коллег и помогает в их обучении."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Отличные коммуникативные навыки и уважение к коллегам."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Постоянно превышает ожидания по качеству выполненной работы."},
    {"ID_reviewer": "0", "ID_under_review": -1, "review": "Готов брать на себя ответственность за сложные проекты."},

    # Отзывы для сотрудника с ID 102 (плохая производительность)
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Часто пропускает сроки выполнения задач."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Недостаток вовлеченности в рабочий процесс."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Невнимателен к деталям и требует постоянного контроля."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Склонен избегать ответственности за ошибки."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Проявляет низкий уровень профессионализма и знаний."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Часто демонстрирует негативное отношение к коллегам."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Редко проявляет инициативу и избегает новых задач."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Низкая мотивация и стремление к развитию."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Отказывается от конструктивной критики и не учится на ошибках."},
    {"ID_reviewer": "0", "ID_under_review": -2, "review": "Часто испытывает трудности с выполнением базовых задач."}
]


# Определение модели User
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

# Определение модели ReviewsData
class ReviewsData(Base):
    __tablename__ = 'reviews_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ID_reviewer = Column(Float, nullable=False)
    ID_under_review = Column(Float, nullable=False)
    review = Column(String, nullable=False)


class NeuralAnalysisRequest(Base):
    __tablename__ = 'neural_analysis_requests'

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_ids = Column(ARRAY(String), nullable=False)
    analysis_status = Column(String, default="pending")  # Статус запроса (например, pending, in_progress, completed)
    analysis_result = Column(ARRAY(String), nullable=True)  # Поле для хранения результатов анализа, если они завершены

# Определение модели SummaryData


# Функция для хэширования пароля
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Создание базы данных и таблиц с проверкой на существование
def create_database():
    Base.metadata.create_all(engine)
    print("Таблицы созданы, если они не существовали ранее.")

# Создание начального пользователя, если его нет
def create_initial_user():
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_user = session.query(User).filter_by(login="hr_manager").first()

    if not existing_user:
        # Захэшировать пароль перед сохранением
        hashed_password = hash_password("scoreworker")
        initial_user = User(login="hr_manager", password=hashed_password)
        session.add(initial_user)
        session.commit()
        print("Начальный пользователь создан.")
    else:
        print("Начальный пользователь уже существует.")

def load_reviews_from_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for review_data in data:
                new_review = ReviewsData(
                    ID_reviewer=review_data['ID_reviewer'],
                    ID_under_review=review_data['ID_under_review'],
                    review=review_data['review']
                )
                session.add(new_review)
        for review_data in perfect_and_bad_data:
            new_review = ReviewsData(
                ID_reviewer=review_data['ID_reviewer'],
                ID_under_review=review_data['ID_under_review'],
                review=review_data['review']
            )
            session.add(new_review)
        session.commit()
        print("Записи добавлены в базу данных.")
    except Exception as e:
        session.rollback()
        print(f"Произошла ошибка при добавлении записей: {e}")


# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    filepath = "review_dataset.json"
    create_database()
    create_initial_user()
    load_reviews_from_json(format_dataset(filepath))
    # load_reviews_from_json("sample_reviews.json")
    print("База данных и начальный пользователь готовы!")
