FROM python:3.4
MAINTAINER Dale Bewley <dale@bewley.net>

RUN pip install Flask==0.10.1
WORKDIR /app
COPY app /app

CMD ["python", "identidock.py"]
