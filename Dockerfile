FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/local/bin

COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt
