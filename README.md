# LMS: платформа онлайн-обучения

Учебный проект на Django REST Framework: курсы, уроки, подписки, платежи
через Stripe, JWT-авторизация, Celery для фоновых задач.

Стек: Django, DRF, PostgreSQL, Redis, Celery, Nginx, Docker Compose,
GitHub Actions.

## Что запускается

Все сервисы описаны в `docker-compose.yaml`:

- `web` - Django + Gunicorn
- `db` - PostgreSQL
- `redis` - брокер для Celery
- `celery` и `celery_beat` - фоновые и периодические задачи
- `nginx` - отдаёт статику и проксирует запросы в `web`

## Запуск локально

1. Скопировать `.env.template` в `.env` и заполнить значения.
   Для локальной работы: `DEBUG=True`, `ALLOWED_HOSTS=localhost,127.0.0.1`.
   Хосты базы и Redis задаёт docker-compose, их можно не заполнять.
2. Запустить всё одной командой:
   ```bash
   docker compose up --build
   ```
3. Создать администратора:
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
4. Документация API: http://localhost/api/docs/

Остановить: `docker compose down`.

## CI/CD

Workflow лежит в `.github/workflows/ci.yml` и запускается при push и PR.
Этапы идут по порядку, при ошибке следующие не запускаются:

1. `test` - тесты
2. `lint` - flake8
3. `build` - сборка Docker-образа (в `main` ещё и публикация на Docker Hub)
4. `deploy` - только в `main`: по SSH обновляется код на сервере,
   скачивается образ и перезапускаются контейнеры

Секреты в настройках репозитория (Settings -> Secrets and variables -> Actions):
`SERVER_HOST`, `SERVER_USER`, `SSH_PRIVATE_KEY`, `SECRET_KEY`,
`DOCKER_USERNAME`, `DOCKER_PASSWORD` (токен Docker Hub).

## Настройка сервера

Ubuntu 24.04:

1. Установить Docker:
   ```bash
   sudo apt install -y docker.io docker-compose-v2
   sudo usermod -aG docker $USER
   ```
2. Создать SSH-ключ без пароля для деплоя, публичную часть добавить в
   `~/.ssh/authorized_keys`, приватную - в секрет `SSH_PRIVATE_KEY`.
3. Открыть в файрволе только порты 22 и 80.
4. Склонировать репозиторий и создать `.env` из шаблона. На сервере:
   `DEBUG=False`, `ALLOWED_HOSTS=<IP сервера>`,
   `DOCKER_IMAGE=<логин Docker Hub>/lms:latest`.
5. Репозиторий образа на Docker Hub сделать публичным.
6. Дальше деплой идёт автоматически при push в `main`.
   После первого деплоя создать администратора командой из пункта 3
   раздела про локальный запуск.

Проверка: `docker compose ps` (все контейнеры `Up`) и страница
http://<IP сервера>/api/docs/.
