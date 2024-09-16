# Use an official Python runtime as the base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE app.settings_production

# Copy the project code into the container
COPY . .

# Install the project dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements-prod.txt

ENTRYPOINT [ "sh", "/code/docker-entrypoint.sh"]
