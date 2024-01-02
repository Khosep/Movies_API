FROM python:3.10

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY run_web.sh run_web.sh
COPY requirements.txt requirements.txt

RUN  apt update && apt install -y netcat-traditional \
     && pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

COPY . .


RUN chmod +x run_web.sh
ENTRYPOINT ["./run_web.sh"]


