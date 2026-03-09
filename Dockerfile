FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /flask_app

# python venv
COPY ./flask_app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# copy needed stuff
COPY .  .

CMD ["gunicorn", "--config", "gunicorn.conf.py", "main:app"]
