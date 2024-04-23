FROM python:3.12.1
WORKDIR rpc_speed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOST="host.docker.internal"

# Settings logging
ENV LEVEL="INFO"
ENV GURU="True"
ENV TRACEBACK="false"

# Settings for RabbitMQ
ENV RABBIT_USER="guest"
ENV RABBIT_PASSWORD="guest"
ENV RABBIT_HOST="host.docker.internal"
ENV RABBIT_PORT="5672"

# Settings for RPCServer
ENV RPC_QUEUE_NAME="speed_rpc_queue"

# Settings for Service
ENV SERVICE_PORT="8005"
ENV BASE_URL="http://${HOST}:${SERVICE_PORT}/"
ENV TG_ADMIN_ID="-1"

# Yandex disk settings
ENV YA_TOKEN=""
ENV YA_CLIENT_ID=""
ENV YA_DIR="ii_speed"
ENV YA_ATTEMPT_COUNT=10

# Building
RUN pip install --upgrade pip  --no-cache-dir
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY rpc_speed .

CMD python main.py