FROM python:3.11-slim

WORKDIR /app

COPY requirements.in .

RUN pip install pip-tools
RUN pip-compile requirements.in -o requirements.txt
RUN pip install -r requirements.txt

COPY settings.toml .

COPY ./app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]