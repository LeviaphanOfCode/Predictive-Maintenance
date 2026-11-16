FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN HOST_MAIN="mirror.yandex" && \
	PATH_MAIN="ru/mirrors/pypi/simple" && \
	HOST_EXTRA="pypi" && \
	PATH_EXTRA="org/simple" && \
	pip install --no-cache-dir \
	-i "https://${HOST_MAIN}.${PATH_MAIN}" \
	--extra-index-url "https://${HOST_EXTRA}.${PATH_EXTRA}" \
	-r requirements.txt

COPY app/ ./app/
COPY models/ ./models/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
