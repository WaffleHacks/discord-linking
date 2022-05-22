#!/bin/sh

FLASK_APP=discord_linking:app flask db migrate
exec gunicorn \
  --access-logfile - \
  --bind '[::]:8000' \
  --worker-tmp-dir /dev/shm \
  --workers "${GUNICORN_WORKERS:-3}" \
  discord_linking:app
