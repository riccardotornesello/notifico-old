FROM python:3-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN adduser -S appuser

RUN apk add --no-cache mariadb-dev build-base
RUN pip install pipenv
RUN chmod u+s /bin/ping

COPY Pipfile* ./
RUN pipenv install --system

COPY . .
RUN mkdir staticfiles
RUN chmod +x docker_entrypoint.sh
RUN chown -R appuser /usr/src/app

USER appuser
ENTRYPOINT ["/usr/src/app/docker_entrypoint.sh"]