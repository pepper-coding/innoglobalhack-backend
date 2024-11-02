import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Float
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

# Определение модели SummaryData
class SummaryData(Base):
    __tablename__ = 'summary_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ID_under_review = Column(Float, nullable=False)
    summary_review = Column(String, nullable=False)

class ReviewsToSummary(Base):
    __tablename__ = 'reviews_to_summary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    reviews_id = Column(String, nullable=False)
    

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
    print("База данных и начальный пользователь готовы!")
