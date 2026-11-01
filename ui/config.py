import os
from dotenv import load_dotenv

# Загружает переменные из файла .env
load_dotenv()

# --- Данные для авторизации (должны быть в .env) ---
BASE_URL = "https://ru.yougile.com"
LOGIN = os.getenv("YOUGILE_LOGIN")
PASSWORD = os.getenv("YOUGILE_PASSWORD")
COMPANY_ID = os.getenv("YOUGILE_COMPANY_ID")



 #коммит для Reguest