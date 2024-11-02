import json
import requests
from collections import Counter
import nltk
from time import sleep

def unify_criteria(all_criteria_lists):
    criteria_count = Counter(elem.lower().strip() for elem in all_criteria_lists if elem)  # Убираем пустые строки
    most_common_criteria = criteria_count.most_common(5)
    return [criteria for criteria, _ in most_common_criteria]

def load_reviews(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reviews = json.load(file)
    return reviews

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
        "system_prompt": "You are a helpful assistant.",
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

def create_variables(criterias):
    file_path = "sample_reviews.json"
    reviews = load_reviews(file_path)

    employee_reviews_map = {}
    for review in reviews:
        employee_id = review['ID_under_review']
        employee_reviews_map.setdefault(employee_id, []).append(review['review'])

    employee_ids = list(employee_reviews_map.keys())
    all_reviews = []

    for employee_id in employee_ids:
        employee_reviews = employee_reviews_map[employee_id]
        unique_reviews = list(set(employee_reviews))
        # print(len(unique_reviews))
        reviews = get_employee_review(employee_id, unique_reviews, criterias)
        sleep(10)
        # print("Оценка сотрудника", employee_id, ":", reviews, "\n\n")

        if reviews:
            all_reviews.append(f"Сотрудник {employee_id}:\n{reviews}")

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

def get_criterias():
    file_path = "sample_reviews.json"
    reviews = load_reviews(file_path)

    employee_reviews_map = {}
    for review in reviews:
        employee_id = review['ID_under_review']
        employee_reviews_map.setdefault(employee_id, []).append(review['review'])

    employee_ids = list(employee_reviews_map.keys())
    all_criteria = []

    for employee_id in employee_ids:
        employee_reviews = employee_reviews_map[employee_id]
        criteria = get_employee_criteria(employee_id, employee_reviews)
        # print("Критерии для сотрудника", employee_id, ":", criteria)

        if criteria:
            criteria = criteria.replace(".", "").replace("\n", "")
            criteria_list = [criterion.strip() for criterion in criteria.split(',') if criterion]
            all_criteria.extend(criteria_list)

    unified_criteria = unify_criteria(all_criteria)
    # print("Объединенные критерии", unified_criteria)
    return unified_criteria

if __name__ == "__main__":
    unified_criteria = get_criterias()
    # print(unified_criteria)
    create_variables(unified_criteria)
