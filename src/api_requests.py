import requests

# URL вашего сервера
url = "http://localhost:8000/get_all_analysis_requests"

# Заголовок с токеном авторизации JWT

# Выполняем GET-запрос
response = requests.get(url)

# Проверка результата
if response.status_code == 200:
    analysis_requests = response.json()
    for request in analysis_requests:
        print("ID запроса:", request["id"])
        print("IDs сотрудников:", request["worker_ids"])
        print("Статус анализа:", request["analysis_status"])
        print("Результат анализа:", request["analysis_result"])
        print("-" * 50)
else:
    print("Ошибка:", response.json().get("error"))
