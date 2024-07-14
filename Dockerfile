
FROM python:3.8-slim

WORKDIR /app

COPY webhook_server.py /app
COPY server-cert.pem /app/server-cert.pem
COPY server-key.pem /app/server-key.pem

RUN pip install flask

CMD ["python", "webhook_server.py"]

