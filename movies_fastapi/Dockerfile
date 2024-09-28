FROM python:3.11.0

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR on
ENV PIP_DISABLE_PIP_VERSION_CHECK on

WORKDIR /usr/src/movies_fastapi

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip  \
    && pip install -r requirements.txt

COPY . .
