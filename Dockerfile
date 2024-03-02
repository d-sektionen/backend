# Use an official Python runtime as the base image
FROM python:3.8

# Set the working directory in the container
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE app.settings_production

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . .

# Define entrypoint script
COPY docker-entrypoint.sh .
ENTRYPOINT [ "sh", "/code/docker-entrypoint.sh"]