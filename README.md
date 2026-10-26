# OpenAI Chat

Небольшое веб-приложение на FastAPI с чат-интерфейсом и интеграцией OpenAI.

## Возможности

- веб-интерфейс без отдельной frontend-сборки;
- API `POST /api/chat` с валидацией истории сообщений;
- `GET /health` для проверки готовности;
- интерактивная OpenAPI-документация на `/docs`;
- тесты, линтер, GitHub Actions и Dockerfile.

## Локальный запуск

Требуется Python 3.12+.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
cp .env.example .env
```

Укажите `CHAT_API_KEY` в окружении или локальном `.env` (сам файл `.env` игнорируется Git).
При необходимости измените модель через `CHAT_MODEL`; по умолчанию используется `gpt-4.1-mini`.

```bash
export CHAT_API_KEY='...'
.venv/bin/uvicorn openai_chat.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

```bash
curl --fail http://127.0.0.1:8000/health
```

## Разработка

```bash
.venv/bin/ruff check .
.venv/bin/pytest
```

## Docker

```bash
docker build -t openai-chat .
docker run --rm -p 8000:8000 -e CHAT_API_KEY openai-chat
```
