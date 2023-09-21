FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt update && apt install -y ffmpeg && apt install -y libmagic1 && apt install -y build-essential

COPY pyproject.toml poetry.lock ./

RUN export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
RUN export FORCE_CMAKE=1

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev


COPY . .

CMD ["python", "bot.py"]
