import pytest
import random
import string
from playwright.sync_api import Page

def создать_уникальное_имя(префикс: str) -> str:
    """
    Генерирует случайное имя, чтобы тесты не мешали друг другу.
    Пример: 'Авто-Проект XYZ123'
    """
    суффикс = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{префикс} {суффикс}"

def test_check_login(logged_in_page: Page):
    """
    Тест 1: Проверяем, что мы действительно на главной странице после входа.
    """
    страница = logged_in_page
    
    # Ищем надпись "Мои задачи" — это признак того, что вход успешен
    элемент_мои_задачи = страница.locator('text="Мои задачи"')
    
    try:
        элемент_мои_задачи.wait_for(state='visible', timeout=15000)
        print("✅ ТЕСТ 1 УСПЕШЕН: Вход подтвержден, надпись 'Мои задачи' видна.")
    except Exception as ошибка:
        страница.screenshot(path="debug_test1_fail.png")
        pytest.fail(f"Не удалось найти надпись 'Мои задачи'. Ошибка: {ошибка}")

def test_create_project(logged_in_page: Page):
    """
    Тест 2: Создаем новый проект.
    """
    страница = logged_in_page
    имя_проекта = создать_уникальное_имя("Авто-Проект")
    print(f"🚀 ЗАПУСК ТЕСТА 2: Пытаемся создать проект с именем '{имя_проекта}'")

    # 1. Находим кнопку "+" или "Создать проект"
    кнопка_создать = страница.locator('button:has-text("+"), button:has-text("Создать проект")').first
    кнопка_создать.wait_for(state='visible', timeout=15000)
    кнопка_создать.click()

    # 2. Находим поле ввода названия
    поле_название = страница.locator('input[placeholder*="название"], input[type="text"]').first
    поле_название.wait_for(state='visible', timeout=15000)
    поле_название.fill(имя_проекта)

    # 3. Находим кнопку "Создать" или "Сохранить" и нажимаем
    кнопка_сохранить = страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first
    кнопка_сохранить.wait_for(state='enabled', timeout=10000)
    кнопка_сохранить.click()

    # 4. ПРОВЕРКА: Ищем на экране название нашего проекта
    локатор_проекта = страница.locator(f'text="{имя_проекта}"')
    try:
        локатор_проекта.wait_for(state='visible', timeout=30000)
        print(f"✅ ТЕСТ 2 УСПЕШЕН: Проект '{имя_проекта}' успешно создан!")
        страница.screenshot(path="debug_test2_success.png")
    except Exception:
        страница.screenshot(path="debug_test2_fail.png")
        pytest.fail(f"Проект '{имя_проекта}' не появился в списке проектов!")

def test_create_board(logged_in_page: Page):
    """
    Тест 3: Создаем доску внутри проекта.
    """
    страница = logged_in_page
    имя_проекта = создать_уникальное_имя("Врем.Проект")
    имя_доски = создать_уникальное_имя("Авто-Доска")
    print(f"🚀 ЗАПУСК ТЕСТА 3: Создаем доску '{имя_доски}' в проекте '{имя_проекта}'")

    # Сначала создаем проект-контейнер
    страница.locator('button:has-text("+"), button:has-text("Создать проект")').first.click()
    страница.locator('input[placeholder*="название"], input[type="text"]').first.fill(имя_проекта)
    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()
    
    # Ждем появления проекта и кликаем на него, чтобы зайти внутрь
    страница.locator(f'text="{имя_проекта}"').wait_for(state='visible', timeout=30000)
    страница.locator(f'text="{имя_проекта}"').first.click()

    # Теперь создаем доску
    кнопка_доска = страница.locator('button:has-text("+"), text="Создать доску"').first
    кнопка_доска.wait_for(state='visible', timeout=15000)
    кнопка_доска.click()

    поле_доска = страница.locator('input[placeholder*="название"], input[type="text"]').first
    поле_доска.wait_for(state='visible', timeout=15000)
    поле_доска.fill(имя_доски)

    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()

    # ПРОВЕРКА
    локатор_доски = страница.locator(f'text="{имя_доски}"')
    try:
        локатор_доски.wait_for(state='visible', timeout=30000)
        print(f"✅ ТЕСТ 3 УСПЕШЕН: Доска '{имя_доски}' создана!")
        страница.screenshot(path="debug_test3_success.png")
    except Exception:
        страница.screenshot(path="debug_test3_fail.png")
        pytest.fail(f"Доска '{имя_доски}' не появилась!")

def test_move_task(logged_in_page: Page):
    """
    Тест 4: Создаем задачу и перетаскиваем её между колонками (Drag & Drop).
    """
    страница = logged_in_page
    имя_проекта = создать_уникальное_имя("Врем.Проект")
    имя_доски = создать_уникальное_имя("Врем.Доска")
    имя_задачи = создать_уникальное_имя("Авто-Задача")
    print(f"🚀 ЗАПУСК ТЕСТА 4: Перемещаем задачу '{имя_задачи}'")

    # --- Подготовка: создаем проект и доску ---
    страница.locator('button:has-text("+"), button:has-text("Создать проект")').first.click()
    страница.locator('input[placeholder*="название"], input[type="text"]').first.fill(имя_проекта)
    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()
    страница.locator(f'text="{имя_проекта}"').wait_for(state='visible', timeout=30000)
    страница.locator(f'text="{имя_проекта}"').first.click()
    
    страница.locator('button:has-text("+"), text="Создать доску"').first.click()
    страница.locator('input[placeholder*="название"], input[type="text"]').first.fill(имя_доски)
    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()
    страница.locator(f'text="{имя_доски}"').wait_for(state='visible', timeout=30000)
    страница.locator(f'text="{имя_доски}"').first.click()

    # --- Создаем задачу в первой колонке ---
    первая_колонка = страница.locator('div[data-testid="column"], div[class*="column"]').first
    кнопка_добавить_задачу = первая_колонка.locator('button:has-text("+"), button:has-text("Создать задачу")').first
    кнопка_добавить_задачу.wait_for(state='visible', timeout=10000)
    кнопка_добавить_задачу.click()

    поле_задача = страница.locator('input[placeholder*="заголовок"], input[type="text"]').first
    поле_задача.wait_for(state='visible', timeout=10000)
    поле_задача.fill(имя_задачи)
    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()

    # --- Ищем задачу и вторую колонку ---
    локатор_задачи = страница.locator(f'text="{имя_задачи}"')
    локатор_задачи.wait_for(state='visible', timeout=20000)

    вторая_колонка = страница.locator('div[data-testid="column"], div[class*="column"]').nth(1)
    
    # --- ГЛАВНОЕ ДЕЙСТВИЕ: Перетаскиваем задачу ---
    локатор_задачи.drag_to(вторая_колонка, force=True)

    # --- ПРОВЕРКА ---
    assert not первая_колонка.locator(f'text="{имя_задачи}"').is_visible(), "ОШИБКА: Задача осталась в первой колонке!"
    assert вторая_колонка.locator(f'text="{имя_задачи}"').is_visible(), "ОШИБКА: Задачи нет во второй колонке!"

    print(f"✅ ТЕСТ 4 УСПЕШЕН: Задача '{имя_задачи}' успешно перемещена!")
    страница.screenshot(path="debug_test4_success.png")

def test_create_department(logged_in_page: Page):
    """
    Тест 5: Создаем отдел (требуется роль администратора).
    """
    страница = logged_in_page
    имя_отдела = создать_уникальное_имя("Авто-Отдел")
    print(f"🚀 ЗАПУСК ТЕСТА 5: Пытаемся создать отдел '{имя_отдела}'")

    # Ищем ссылку "Моя компания" или "Компания"
    ссылка_компания = страница.locator('a:has-text("Моя компания"), a:has-text("Компания"), button:has-text("Компания")').first
    
    # Если ссылки нет (нет прав), пропускаем тест
    if not ссылка_компания.is_visible():
        print("⚠️ ИНФО: Нет доступа к разделу компании. Пропускаем тест отдела.")
        pytest.skip("Нет прав или элемента для создания отдела.")

    ссылка_компания.wait_for(state='visible', timeout=15000)
    ссылка_компания.click()

    кнопка_отдел = страница.locator('button:has-text("+"), button:has-text("Создать отдел"), button:has-text("Добавить отдел")').first
    кнопка_отдел.wait_for(state='visible', timeout=20000)
    кнопка_отдел.click()

    поле_отдел = страница.locator('input[placeholder*="название"], input[type="text"]').first
    поле_отдел.wait_for(state='visible', timeout=10000)
    поле_отдел.fill(имя_отдела)

    страница.locator('button:has-text("Создать"), button:has-text("Сохранить")').first.click()

    # ПРОВЕРКА
    локатор_отдела = страница.locator(f'text="{имя_отдела}"')
    try:
        локатор_отдела.wait_for(state='visible', timeout=30000)
        print(f"✅ ТЕСТ 5 УСПЕШЕН: Отдел '{имя_отдела}' создан!")
        страница.screenshot(path="debug_test5_success.png")
    except Exception:
        страница.screenshot(path="debug_test5_fail.png")
        pytest.fail(f"Отдел '{имя_отдела}' не появился в списке!")