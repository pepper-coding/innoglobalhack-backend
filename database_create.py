import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Настройка соединения с PostgreSQL
DATABASE_URL = "postgresql://postgres-username:postgres-password@26.136.157.33:5432/innoglobalhack"

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

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    create_database()
    create_initial_user()
    print("База данных и начальный пользователь готовы!")
