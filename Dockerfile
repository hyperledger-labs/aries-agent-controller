# Use an official Python runtime as a parent image
FROM python:3.11-slim-buster as production

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
  && apt-get -y install curl build-essential libpq-dev gcc git make \
  && apt-get clean

# Install Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Copy project files into the docker image
COPY . /app

# Install project dependencies
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]