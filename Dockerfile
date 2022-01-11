# base image start from python and version like python:version
FROM python:3


ENV PYTHONUNBUFFERED 1

# working directory
WORKDIR /app        

# adding all things (.) to app
ADD . /app

# copying requirements.py to app folder
COPY ./requirements.txt /app/requirements.txt

# it will install requirements.txt
RUN pip3 install -r requirements.txt

# copying all things to app folder
COPY . /app