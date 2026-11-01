import pytest
import requests
from playwright.sync_api import sync_playwright
from config import BASE_URL, AUTH_TOKEN

# --- API ФИКСТУРЫ ---
@pytest.fixture(scope="session")
def api_session():
    session = requests.Session()
    session.base_url = BASE_URL
    return session

@pytest.fixture(scope="session")
def auth_token(api_session):
    if not AUTH_TOKEN:
        pytest.fail("В config.py не указан AUTH_TOKEN. Пожалуйста, вставьте туда ваш ключ.")
    return AUTH_TOKEN

