import requests
import hashlib

# Указываем URL вашего API
url = "http://localhost:8000/get_all"

# Данные для авторизации
login = "hr_manager"
password = "scoreworker"

# Хэшируем пароль с помощью SHA-256
hashed_password = hashlib.sha256(password.encode()).hexdigest()
print(hashed_password)
# Подготавливаем данные для запроса
data = {
    "worker_ids" :["31", "20906"]
}

# Выполняем POST-запрос на авторизацию
response = requests.post(url, data)

# Проверяем статус ответа
if response.status_code == 200:
    # Если авторизация успешна, выводим токен
    print(response.text)
else:
    # Если произошла ошибка, выводим сообщение
    print("Ошибка авторизации:", response.json().get("msg"))
