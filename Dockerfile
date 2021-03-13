FROM python:3.7

ENV PYTHONUNBUFFERED 1
WORKDIR /opt/api

COPY ./requirements.txt ./
COPY ./requirements-test.txt ./
RUN pip install --upgrade pip==21.0.1
RUN pip install -r ./requirements.txt -r requirements-test.txt
