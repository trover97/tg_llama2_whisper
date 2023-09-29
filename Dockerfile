FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONHASHSEED=random
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100


WORKDIR /app

COPY pyproject.toml poetry.lock ./

ENV CMAKE_ARGS="-DLLAMA_CUBLAS=on"
ENV FORCE_CMAKE=1
ENV LLAMA_CUBLAS=1


# Update the package list and install necessary tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-venv python3.10-dev python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt update && apt install -y ffmpeg libmagic1 libcudnn8 libcudnn8-dev libcublas11


RUN python3.10 -m pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev


COPY . .

CMD ["python3.10", "bot.py"]
