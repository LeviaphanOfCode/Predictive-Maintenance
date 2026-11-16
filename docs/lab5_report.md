## Лабораторная работа №5: контейнеризация, Docker
 
### Назначение контейнера
Сервис инференса из ЛР №4 упакован в Docker-образ на базе `python:3.11-slim`. В образ входят код `app/` и артефакты модели `models/weights.npz`. Тренировочная часть (`app/ml/pipeline.py`, `app/core/contracts.py`, MLflow, sklearn, pandera) в образ не входит.
 
### Структура артефактов
- `Dockerfile` - многослойная инструкция сборки образа;
- `.dockerignore` - исключение `venv/`, `data/`, `mlruns/`, кэшей из контекста сборки;
- `requirements.txt` - зафиксированные версии зависимостей рантайма;
- `models/weights.npz` - веса модели (отслеживаются через DVC);
- `app/main.py` - точка входа ASGI, загрузка движка через `lifespan`;
- `tests/test_container.py` - smoke-тесты доступности контейнера.
 
### Инструкция по запуску
Для запуска необходим установленный Docker и свободный порт 8000 на хосте.
 
```bash
# Сборка образа с семантическим тегом
docker build -t pump-predictor:v1.4.0 .
 
# Запуск контейнера с пробросом порта
docker run -d -p 8000:8000 --name pump-api pump-predictor:v1.4.0
 
# Проверка healthcheck
curl http://localhost:8000/health
 
# Smoke-тесты
pytest tests/test_container.py -v
 
# Остановка и удаление контейнера
docker stop pump-api && docker rm pump-api