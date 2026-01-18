FROM python:3.13-slim-bookworm

WORKDIR /usr/src/english-boost

RUN apt-get update \
    && apt-get install -y netcat-openbsd \
    && pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r$//g' /usr/src/english-boost/entrypoint.sh
RUN chmod +x /usr/src/english-boost/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "english_app.wsgi:application"]