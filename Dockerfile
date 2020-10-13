FROM python:3.7

ENV PYTHONUNBUFFERED 1
WORKDIR /opt/apiweb

COPY ./requirements.txt ./
COPY ./test-requirements.txt ./
RUN pip install -r ./requirements.txt -r test-requirements.txt
