
import requests


url = "https://sms.ru/auth/check?api_id=687BB7A9-F4B2-8B0C-4E8A-1F9B50E5FEC8&json=1"

response = requests.get(url)

# Проверка результата
if response.status_code == 200:
    data = response.json()
    print(data)
