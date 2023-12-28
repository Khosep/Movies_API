FROM python:3.10

WORKDIR /opp/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements_etl.txt requirements_etl.txt

RUN  pip install --upgrade pip && pip install --no-cache-dir -r requirements_etl.txt


COPY . .

ENTRYPOINT ["python", "main.py"]


