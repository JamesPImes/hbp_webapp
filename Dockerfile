FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# This line is required because requirements.txt includes some projects that are
# installed as `git+<...>`, which fail  if we don't install git first.
RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
# Copy .dockerenv to overwrite .env (only within the Docker image),
# so use only .dockerenv for a Docker build.
COPY .dockerenv /app/.env

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
