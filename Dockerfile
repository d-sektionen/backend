# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /code

# Set build args
#ARG UID
#ARG GID

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings_production
ENV UID=1002
ENV GID=1002

# Copy the requirements file into the container
COPY production.txt .
COPY development.txt .
COPY docker-entrypoint.sh .

# Install the project dependencies
RUN pip install --no-cache-dir -r production.txt

# Copy the project code into the container
COPY . .

# Set permissions
RUN chown -R ${UID}:${GID} .
RUN chmod -R 755 .

# Expose the port that the Django app will run on
EXPOSE 8000

# Switch to a non-root user
USER ${UID}:${GID}

# Run migration
RUN chmod +x docker-entrypoint.sh

# Define the command to run the Django app
#CMD python manage.py runserver 127.0.0.1:8000
