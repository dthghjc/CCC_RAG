FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY app /opt/app/

ENTRYPOINT ["python3", "app/main.py"]