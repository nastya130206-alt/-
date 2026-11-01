import os
from dotenv import load_dotenv

load_dotenv()  # Загружает переменные из файла .env

BASE_URL = "https://ru.yougile.com"
LOGIN = os.getenv("YOUGILE_LOGIN")
PASSWORD = os.getenv("YOUGILE_PASSWORD")
COMPANY_ID = os.getenv("YOUGILE_COMPANY_ID")
AUTH_TOKEN = "23bAedBJ9l_tQ-LHlnYlZgd3V24ouSYohBQWprXcIHEfu60M9CqnwnfQZUVtU08e"
# Для UI тестов можно вынести селекторы, но лучше использовать locators внутри тестов или в отдельном файле locators.p