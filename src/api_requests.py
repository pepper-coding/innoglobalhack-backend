import requests
import hashlib

# Указываем URL вашего API
url = "http://localhost:8000/login"

# Данные для авторизации
login = "hr_manager"
password = "scoreworker"

# Хэшируем пароль с помощью SHA-256
hashed_password = hashlib.sha256(password.encode()).hexdigest()
print(hashed_password)
# Подготавливаем данные для запроса
data = {
    "login": login,
    "password": hashed_password
}

# Выполняем POST-запрос на авторизацию
response = requests.post(url, json=data)

# Проверяем статус ответа
if response.status_code == 200:
    # Если авторизация успешна, выводим токен
    token = response.json().get("access_token")
    print("Токен доступа:", token)
else:
    # Если произошла ошибка, выводим сообщение
    print("Ошибка авторизации:", response.json().get("msg"))
