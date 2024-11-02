get_all :       /get_all    GET
    {"worker_ids": ["...","...","...","..."]} - string

get_selected :           /get_selected_requests     POST    {"worker_ids": ["...","...","...","..."]} - string
    запуск нейронки


get_request_by_id:      /get_request_by_id  GET
    {"worker_id": "айди" - string,
    "user_feedback:": "отзыв" - string}
