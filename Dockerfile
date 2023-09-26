FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN export CMAKE_ARGS="-DLLAMA_CUBLAS=on"
RUN export FORCE_CMAKE=1

# Update the package list and install necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt update && apt upgrade -y && apt install -y ffmpeg && apt install -y libmagic1

RUN apt install -y libcudnn8 && apt install -y libcudnn8-dev


RUN python3.10 -m pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev


COPY . .

CMD ["python3.10", "bot.py"]
