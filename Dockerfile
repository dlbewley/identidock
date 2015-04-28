FROM python:3.4
MAINTAINER Dale Bewley <dale@bewley.net>

RUN groupadd -r uwsgi && useradd -r -g uwsgi uwsgi
RUN pip install Flask==0.10.1 uWSGI==2.0.8 requests==2.5.1
WORKDIR /app
COPY app /app
COPY cmd.sh /

EXPOSE 5000 9090 9191
USER uwsgi

CMD ["/cmd.sh"]
