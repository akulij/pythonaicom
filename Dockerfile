FROM python:latest

WORKDIR /app

COPY ["pyproject.toml", "config.toml", "poetry.lock*", "./"]

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "main.py"]
