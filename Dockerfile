FROM python:3.10-slim

# Install netcat to use 'nc' in entrypoint.sh
RUN apt-get update && apt-get install -y netcat-openbsd
RUN apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


RUN chmod +x entrypoint.sh


ENTRYPOINT ["sh", "./entrypoint.sh"]
