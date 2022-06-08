FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

RUN apt-get update && \
    apt-get upgrade -y

RUN pip install --upgrade pip && \
    pip install --no-cache-dir Flask gunicorn

RUN adduser --disabled-password app
USER app

WORKDIR /mocked_integrations

COPY --chown=app ./mocked_integrations mocked_integrations

COPY --chown=app --chmod=775 ./entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
