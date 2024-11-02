import pandas as pd
import json

def format_dataset(path_file):
    data = pd.read_json(path_file)

    # Удаление записей, где ID_reviewer равен ID_under_review или не является числом
    data['ID_reviewer'] = pd.to_numeric(data['ID_reviewer'], errors='coerce')  # Преобразуем в числовой формат
    cleaned_data = data[data['ID_reviewer'].notna() & (data['ID_reviewer'] != data['ID_under_review'])]

    # Сортировка данных
    sorted_data = cleaned_data.sort_values(by='ID_under_review', ascending=False)

    # Преобразование данных в список словарей
    records = sorted_data.to_dict(orient='records')

    # Сохранение в файл в стандартном формате JSON
    with open(f"sorted_{path_file}", 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    return f"sorted_{path_file}"

# Вызов функции
