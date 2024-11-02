import os
import requests
from collections import Counter
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dotenv import load_dotenv
from database_create import ReviewsData
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Создание движка базы данных и сессии
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def unify_criteria(all_criteria_lists):
    criteria_count = Counter(elem.lower().strip() for elem in all_criteria_lists if elem)  # Убираем пустые строки
    most_common_criteria = criteria_count.most_common(5)
    return [criteria for criteria, _ in most_common_criteria]

def get_reviews_from_db(employee_id):
    # Создаем сессию для работы с базой данных
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Выполняем запрос к базе данных для получения отзывов по заданному ID
        query = select(ReviewsData).where(ReviewsData.ID_under_review == employee_id)
        result = session.execute(query)
        reviews = [row.review for row in result.scalars()]  # Извлекаем отзывы из результата
        return reviews
    except Exception as e:
        print(f"Произошла ошибка при извлечении отзывов: {e}")
        return []
    finally:
        session.close()  # Закрываем сессию


def prepare_initial_prompt(employee_id, employee_reviews):
    prompt = (
        "Ниже приведены отзывы о сотруднике. На основе этих отзывов предложите критерии, "
        "по которым можно оценить этого сотрудника. Укажите не более 5 критериев оценки, "
        "которые будут наиболее важными для его профессиональной оценки. "
        "В ответе содержатся только названия критериев, без номеров. "
        "Количество критериев не указывать. Вывод критериев в одной строке.\n\n"
        f"Сотрудник ID: {employee_id}\n"
        "Пример:\n\n"
    )

    unique_reviews = list(set(employee_reviews))[:5]
    for i, review in enumerate(unique_reviews, start=1):
        prompt += f"Отзыв {i}: {review}\n"

    prompt += (
        "\nУкажите критерии оценки сотрудника в формате: \"Критерий 1, Критерий 2, ...\". "
        "Остального текста быть не должно. "
        "Не выводить Ответ и Результат."
    )

    return prompt

def prepare_reviews_prompt(employee_id, employee_reviews, criterias):
    prompt = (
        "Ниже приведены критерии и отзывы о сотруднике. На основе отзывов составьте оценку по каждому критерию от 1 до 5. "
        "Формат: 'Критерий: Оценка'. Если оценка меньше 4, дайте конкретный совет по улучшению. "
        "Если оценка 5, просто укажите, что это высокий уровень. "
        "Избегайте имен, примеров и лишних пояснений. "
        "Результат должен содержать только оценки, советы и краткий вывод в формате: 'Краткий вывод: [ваш вывод]'. "
        "Краткий вывод не должен превышать два предложения.\n\n"
        f"Критерии:\n{', '.join(criterias)}\n\n"
        f"Сотрудник ID: {employee_id}\n"
        f"Отзывы: {', '.join(employee_reviews)}\n\n"
    )

    return prompt

def get_employee_review(employee_id, employee_reviews, criteria):
    prompt = prepare_reviews_prompt(employee_id, employee_reviews, criteria)

    url = "https://vk-scoreworker-case.olymp.innopolis.university/generate"
    data = {
        "prompt": prompt,
        "apply_chat_template": True,
        "system_prompt": "Вы помощник, который выявляет критерии оценки сотрудников.",
        "max_tokens": 350,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.5,
        "presence_penalty": 0.5,
        "n": 1
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data.strip() if response_data else None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ошибка: {e}")
    except json.JSONDecodeError:
        print("Не удалось декодировать JSON, полученный ответ:", response.text)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return None

def create_variables(criterias, employee_ids):
    all_reviews = []
    all_employee = []
    for employee_id in employee_ids:
        employee_reviews = get_reviews_from_db(employee_id)
        unique_reviews = list(set(employee_reviews))

        while True:
            reviews = get_employee_review(employee_id, unique_reviews, criterias)

            # Приводим критерии и отзывы к нижнему регистру для сравнения
            reviews_lower = reviews.lower() if reviews else ""
            criterias_lower = [criterion.lower() for criterion in criterias]

            # Проверяем наличие всех критериев в результате
            if all(criterion in reviews_lower for criterion in criterias_lower):
                break  # Выходим из цикла, если все критерии присутствуют
        print("Оценка сотрудника", employee_id, ":", reviews, "\n\n")
        if reviews:
            all_reviews.append(reviews)
            all_employee.append(employee_id)

    for elem in all_reviews:
        print(f"{elem}\n\n")

def get_employee_criteria(employee_id, employee_reviews):
    prompt = prepare_initial_prompt(employee_id, employee_reviews)

    url = "https://vk-scoreworker-case.olymp.innopolis.university/generate"
    data = {
        "prompt": [prompt],
        "apply_chat_template": False,
        "system_prompt": "Вы помощник, который выявляет критерии оценки сотрудников.",
        "max_tokens": 300,
        "n": 1,
        "temperature": 0.0
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        response_data = response.json()
        return response_data.strip() if response_data else None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP ошибка: {e}")
    except json.JSONDecodeError:
        print("Не удалось декодировать JSON, полученный ответ:", response.text)
    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return None

def get_criterias(selected_employee_ids):
    all_criteria = []

    for employee_id in selected_employee_ids:
        employee_reviews = get_reviews_from_db(employee_id)
        criteria = get_employee_criteria(employee_id, employee_reviews)

        if criteria:
            criteria = criteria.replace(".", "").replace("\n", "")
            criteria_list = [criterion.strip() for criterion in criteria.split(',') if criterion]
            all_criteria.append((employee_id, criteria_list))  # Храним кортеж (ID, критерии)

    unified_criteria = unify_criteria([criterion for _, criteria_list in all_criteria for criterion in criteria_list])
    return unified_criteria, all_criteria  # Возвращаем также все критерии для ID

def get_employee_ids():
    query = text("SELECT DISTINCT ID_under_review FROM reviews_data")
    result = session.execute(query)
    employee_ids = [row['ID_under_review'] for row in result]
    return employee_ids

if __name__ == "__main__":
    selected_employee_ids = ["65282", "57549", "113201"]  # Замените на ваши ID
    unified_criteria, all_criteria = get_criterias(selected_employee_ids)
    create_variables(unified_criteria, selected_employee_ids)
