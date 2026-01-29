# Use a slim python runtime to reduce image size
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.app.settings_production

# Copy the requirements file into container
COPY requirements.txt requirements.production.txt ./

# Install build tools and project dependencies, remove tools and cache after.
RUN apt update && apt upgrade -y && \
    apt install gcc musl-dev -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.production.txt && \
    apt clean autoclean && \
    apt autoremove --purge apt pip gcc musl-dev -y --allow-remove-essential && \
    rm -rf /var/lib/{apt,dpkg,cache,log,lists} ./requirements*.txt

# Copy over rest of the project after installing deps to optimize rebuilds
COPY backend.uwsgi.ini /etc/uwsgi/backend.uwsgi.ini
COPY manage.py .
COPY backend ./backend
COPY docker-entrypoint.sh .

ENTRYPOINT [ "sh", "/code/docker-entrypoint.sh"]
