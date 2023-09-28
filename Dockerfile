FROM python:latest

WORKDIR /app

COPY ["pyproject.toml", "config.toml", "poetry.lock*", "./"]

RUN python -m pip install poetry

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "main.py"]
