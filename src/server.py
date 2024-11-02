from flask import Flask, jsonify, request
from flask_cors import CORS

from config import DATABASE_URL

app = Flask(__name__)
app.debug = True
# Разрешаем CORS для всех доменов
CORS(app)

# Пример данных для демонстрации
workers_data = {
    "worker_ids": ["worker_1", "worker_2", "worker_3", "worker_4"],
}

summary_data = {
    "worker_1": "Отличный работник, быстро выполняет задачи.",
    "worker_2": "Умеет работать в команде, отзывчивый.",
    "worker_3": "Не всегда соблюдает сроки, но хорошо разбирается в вопросах.",
    "worker_4": "Требует дополнительного обучения, но проявляет интерес."
}

reviews_data = {
    "worker_1": {"Отличный работник, быстро выполняет задачи.", "Бла бла 1", "Бла бла 2"},
    "worker_2": {"Умеет работать в команде, отзывчивый.", "Бла бла 1", "Бла бла 2"},
    "worker_3": {"Не всегда соблюдает сроки, но хорошо разбирается в вопросах.", "Бла бла 1", "Бла бла 2"},
    "worker_4": {"Требует дополнительного обучения, но проявляет интерес.", "Бла бла 1", "Бла бла 2"},
}

@app.route('/get_all', methods=['GET'])
def get_all_workers():
    return jsonify(workers_data)

@app.route('/get_summary_selected', methods=['POST'])
def get_summary_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    for worker_id in worker_ids:
        if worker_id in summary_data:
            responses.append({"worker_id": worker_id, "user_summary": summary_data[worker_id]})
        else:
            responses.append({"worker_id": worker_id, "user_summary": "Генерирую сводку"})
    print(responses)
    return jsonify(responses)


@app.route('/get_review_selected', methods=['POST'])
def get_review_selected():
    worker_ids = request.json.get("worker_ids", [])
    responses = []
    for worker_id in worker_ids:
        if worker_id in reviews_data:
            # Преобразуем множество в строку для ответа
            user_feedback = list(reviews_data[worker_id])  # Преобразуем множество в список
            responses.append({"worker_id": worker_id, "user_feedback": user_feedback})
        else:
            responses.append({"worker_id": worker_id, "user_feedback": "Генерирую сводку"})
    return jsonify(responses)

# Запуск приложения
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
