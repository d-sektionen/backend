# Pinned uv release; Dependabot keeps it up to date.
FROM ghcr.io/astral-sh/uv:0.13.8 AS uv

# Use a slim python runtime to reduce image size
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.app.settings_production
# Keep the virtual environment outside /code and use the image's own Python.
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV UV_PYTHON_DOWNLOADS=never
ENV PATH="/opt/venv/bin:$PATH"

# Install the locked production dependencies. uv and the project files are
# only mounted for this step, so none of them end up in the image.
RUN --mount=from=uv,source=/uv,target=/bin/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    apt update && apt upgrade -y && \
    uv sync --locked --no-dev --group production --no-cache && \
    apt clean autoclean && \
    apt autoremove --purge apt -y --allow-remove-essential && \
    rm -rf /var/lib/{apt,dpkg,cache,log,lists}

# Copy over rest of the project after installing deps to optimize rebuilds
COPY gunicorn.conf.py .
COPY manage.py .
COPY backend ./backend
COPY docker-entrypoint.sh .

ENTRYPOINT [ "sh", "/code/docker-entrypoint.sh"]
