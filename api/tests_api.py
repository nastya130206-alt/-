import pytest
import json
from config import BASE_URL

def safe_json_response(response, expected_status, context=""):
    """Универсальная проверка ответа: статус и валидный JSON."""
    if response.status_code != expected_status:
        pytest.fail(
            f"[{context}] ОШИБКА: Ожидался статус {expected_status}, пришел {response.status_code}.\n"
            f"Тело ответа: {response.text[:300]}"
        )

    try:
        data = response.json()
        if data is None:
            pytest.fail(f"[{context}] Сервер вернул пустой ответ (None).")
        return data
    except json.JSONDecodeError:
        pytest.fail(
            f"[{context}] Ответ сервера не является валидным JSON:\n{response.text[:300]}"
        )

# --- ТЕСТ 1: Список проектов ---
def test_1_get_projects_list(api_session, auth_token):
    # 1. Запрос
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = api_session.get(f"{BASE_URL}/api-v2/projects", headers=headers)

    # 2. Проверка ответа
    data = safe_json_response(response, 200, "Get Projects List")

    # 3. Получаем список
    projects = data.get("content") if isinstance(data, dict) else data

    # 4. Проверки
    assert isinstance(projects, list), "Ответ не является списком"
    assert len(projects) > 0, "Список пуст"

    first_project = projects
    
    # Первый элемент из списка проектов
    first_project = projects[0]

    # Остальные проверки остаются без изменений
    assert isinstance(first_project, dict), "Первый элемент не словарь"
    assert "title" in first_project, "Нет поля title"
    assert "id" in first_project, "Нет поля id"

    print(f"✅ Тест пройден: {first_project['title']}")

 
# --- ТЕСТ 2: Обработка пустых/некорректных полей (Валидация) ---
def test_2_invalid_fields_handling(api_session, auth_token):
    """
    Проверяет, что API корректно отклоняет запросы с:
    1. Пустым названием (title: "")
    2. Лишним полем (description), которого нет в схеме
    """
    headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    payload = {
        "title": "", 
        "description": "Дипломная работа для тестирования"
    }
    
    response = api_session.post(f"{BASE_URL}/api-v2/projects", json=payload, headers=headers)
    
    data = safe_json_response(response, 400, "Invalid Fields Handling")
    
    assert "message" in data, f"В ответе об ошибке отсутствует поле 'message'. Данные: {data}"
    
    messages = data["message"]
    
    # Нормализуем сообщения: если пришла строка, делаем из неё список
    if isinstance(messages, str):
        messages = [messages]
    
    title_error_found = any("title should not be empty" in msg.lower() for msg in messages)
    assert title_error_found, f"Не найдена ошибка про пустой title. Получено: {messages}"
    
    desc_error_found = any("property description should not exist" in msg.lower() for msg in messages)
    assert desc_error_found, f"Не найдена ошибка про лишнее поле description. Получено: {messages}"
    
    print(f"✅ Тест 2 пройден. Корректно обработаны ошибки валидации: {messages}")

# --- ТЕСТ 3: Получение проекта по ID ---
def test_3_get_project_by_id(api_session, auth_token):
   """
    Проверяет получение конкретного проекта по известному ID.
    Использует ID, предоставленный пользователем: 8ce0b173-833b-4703-b4cb-f42b0167612a
    """
   project_id = "8ce0b173-833b-4703-b4cb-f42b0167612a"
   headers = {"Authorization": f"Bearer {auth_token}"}
    
   response = api_session.get(f"{BASE_URL}/api-v2/projects/{project_id}", headers=headers)
    
   data = safe_json_response(response, 200, "Get Project By ID")
    
    # Если API возвращает сам объект сразу, data уже будет словарем проекта.
    # Если возвращает обертку, нужно проверить. Обычно для GET /projects/{id} возвращают объект.
   project = data if isinstance(data, dict) else (data.get("content") if isinstance(data, dict) else None)
    
    # Дополнительная защита, если вдруг данные пришли списком (редко для одиночного GET)
   if isinstance(project, list):
        project = project 
        
   assert project is not None, "Не удалось извлечь данные проекта из ответа"
   assert "id" in project, f"У проекта отсутствует поле 'id'. Данные: {project}"
   assert project["id"] == project_id, f"ID полученного проекта не совпадает с запрошенным. Ожидалось: {project_id}, Получено: {project['id']}"
   assert "title" in project, f"У проекта отсутствует поле 'title'. Данные: {project}"
    
   print(f"✅ Тест 3 пройден. Получен проект с ID: {project_id}")

# --- ТЕСТ 4: на получение ОДНОГО сотрудника по ID  ---

def test_get_user_by_id(api_session, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    # Берем ID из скриншота (Анастасия)
    target_user_id = "ba974f80-6a10-4837-a899-02d5503b02af"
    
    # 1. Формируем URL с подстановкой ID
    url = f"{BASE_URL}/api-v2/users/{target_user_id}"
    response = api_session.get(url, headers=headers)
    
    # 2. Проверяем статус (для существующего ID это 200, для несуществующего 404)
    assert response.status_code == 200, f"Ожидался статус 200, получен: {response.status_code}"
    
    user_data = response.json()
    
    # 3. ВАЖНО: Эндпоинт получения ОДНОГО пользователя обычно возвращает сразу объект,
    # а не обертку {"content": [...]}. Поэтому мы НЕ делаем user_data.get("content").
    
    assert "id" in user_data, "В ответе отсутствует ID пользователя"
    assert user_data["id"] == target_user_id, "Вернулся ID другого пользователя!"
    assert "email" in user_data, "В ответе отсутствует email"
    assert "realName" in user_data, "В ответе отсутствует realName"
    
    print(f"✅ Тест пройден. Найден пользователь: {user_data['realName']} ({user_data['email']})")

# --- ТЕСТ 5: Несуществующий проект ---
def test_5_get_project_not_found(api_session, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    fake_id = "00000000-0000-0000-0000-000000000000"
    
    response = api_session.get(f"{BASE_URL}/api-v2/projects/{fake_id}", headers=headers)
    
    assert response.status_code == 404, f"Ожидался статус 404, пришел {response.status_code}"
    
    try:
        data = response.json()
    except json.JSONDecodeError:
        pytest.fail("Ответ на ошибку 404 не является валидным JSON")
    
    assert "message" in data, "В ответе об ошибке отсутствует поле 'message'"
    assert "Проект не найден" in str(data.get("message", "")), f"Текст ошибки не совпадает: {data.get('message')}"
    
    print(f"✅ Тест 5 пройден. Корректная обработка несуществующего ID.")


    #коммит для Reguest