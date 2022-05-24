FROM python:3.10-slim as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1

# Update global dependencies
RUN apt-get update && \
    apt-get upgrade -y


# Export dependencies from poetry
FROM base as export-dependencies

# Install poetry
RUN pip install --no-cache-dir poetry

# Export dependencies in requirements.txt format
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt -o requirements.txt --without-hashes


# Install dependencies
FROM base as dependencies

# System build dependencies
RUN apt-get install -y --no-install-recommends build-essential git libpq-dev

# Copy dependencies specification
COPY --from=export-dependencies /requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --prefix=/dependencies --no-warn-script-location


# Project files
FROM scratch as project

COPY ./discord_linking discord_linking
COPY ./migrations migrations



# Generate CSS
FROM node:16-alpine as css

# Copy required files
COPY package.json ./package.json
COPY yarn.lock ./yarn.lock
COPY postcss.config.js ./postcss.config.js
COPY tailwind.config.js ./tailwind.config.js

# Install NPM dependencies
RUN yarn install

# Copy project files to parse from
COPY discord_linking ./discord_linking
COPY static ./static

# Generate the CSS
RUN yarn css


# The final app
FROM base

# Install libpq
RUN apt-get install -y --no-install-recommends libpq-dev

# Switch to a new user
RUN adduser --disabled-password app
USER app

EXPOSE 8000/tcp

WORKDIR /discord-linking

# Copy over dependencies from other steps
COPY --from=dependencies --chown=app /dependencies /usr/local
COPY --from=css --chown=app /bundle.css ./discord_linking/static/

# Copy application source
COPY --chown=app discord_linking ./discord_linking
COPY --chown=app migrations ./migrations

COPY --chown=app --chmod=775 entrypoint.sh ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
