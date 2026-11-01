import os
import pytest
from playwright.sync_api import Page, sync_playwright
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем данные для входа
EMAIL = os.getenv("YOUGILE_EMAIL")
PASSWORD = os.getenv("YOUGILE_PASSWORD")
BASE_URL = os.getenv("YOUGILE_BASE_URL", "https://ru.yougile.com")

@pytest.fixture(scope="function")
def logged_in_page():
    """
    Фикстура для подготовки браузера и входа в систему.
    Возвращает объект страницы (page) с уже авторизованным пользователем.
    """
    with sync_playwright() as p:
        # Запускаем браузер в видимом режиме (headless=False), чтобы видеть процесс
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print("--- ЭТАП 1: Открываем страницу входа ---")
        page.goto(BASE_URL)

        # ВАЖНО: Используем .first(), так как на странице может быть несколько одинаковых полей.
        # Это исправляет ошибку strict mode violation.
        
        print("--- ЭТАП 2: Ищем поле Email (берем первое попавшееся) ---")
        email_input = page.locator('input[type="email"], input[placeholder*="email"]')
        email_input.first.wait_for(state='visible', timeout=45000)
        
        print("--- ЭТАП 3: Ищем поле Пароль (берем первое попавшееся) ---")
        password_input = page.locator('input[type="password"], input[placeholder*="пароль"]')
        password_input.first.wait_for(state='visible', timeout=45000)

        print("--- ЭТАП 4: Вводим данные и нажимаем Войти ---")
        email_input.first.fill(EMAIL)
        password_input.first.fill(PASSWORD)

        login_btn = page.locator('button:has-text("Войти"), button[type="submit"]')
        login_btn.first.wait_for(state='visible', timeout=10000)
        login_btn.first.click()

        print("--- ЭТАП 5: Ждем появления главного экрана ---")
        my_tasks_locator = page.locator('text="Мои задачи"')
        try:
            my_tasks_locator.wait_for(state='visible', timeout=90000)
            print("--- УСПЕХ: Пользователь успешно вошел в систему ---")
        except Exception as e:
            page.screenshot(path="debug_login_failed.png")
            browser.close()
            pytest.fail(f"Не удалось войти в систему: {e}")

        yield page
        
        browser.close()



 #коммит для Reguest