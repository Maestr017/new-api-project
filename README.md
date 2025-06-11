# Task Manager API

RESTful API для управления задачами с поддержкой регистрации, авторизации и аутентификации пользователей.

## Описание

Этот проект реализует backend-сервис для работы с задачами:
- Создание, редактирование, удаление и просмотр задач
- Регистрация новых пользователей
- Вход и выход (аутентификация)
- Управление правами доступа

Используются технологии:
- FastAPI — веб-фреймворк
- Alembic — миграции базы данных
- pytest — тестирование

## Установка

```bash
git clone https://github.com/yourusername/task-manager-api.git
cd task-manager-api
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Документация API

Автоматическая документация доступна по адресу:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Использование

Основные эндпоинты:

- `POST /register` — регистрация пользователя
- `POST /login` — вход и получение токена
- `GET /tasks` — получение списка задач (требуется авторизация)
- `POST /tasks` — создание новой задачи
- `PUT /tasks/{task_id}` — обновление задачи
- `DELETE /tasks/{task_id}` — удаление задачи

Пример запроса для создания задачи:

```bash
curl -X POST "http://localhost:8000/tasks" \
-H "Authorization: Bearer <your_token>" \
-H "Content-Type: application/json" \
-d '{"title": "Новая задача", "description": "Описание задачи"}'
```

## Миграции базы данных

Для создания и применения миграций используйте Alembic:

```bash
alembic revision --autogenerate -m "Описание миграции"
alembic upgrade head
```

## Конфигурация

- `alembic.ini` — настройки Alembic для миграций
- `pytest.ini` — настройки pytest

Если требуется, создайте `.env` файл для переменных окружения (например, строка подключения к БД, секретные ключи).