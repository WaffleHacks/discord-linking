#!/bin/sh

exec gunicorn \
  --access-logfile - \
  --bind '[::]:8000' \
  --worker-tmp-dir /dev/shm \
  --workers "${GUNICORN_WORKERS:-3}" \
  mocked_integrations:app
