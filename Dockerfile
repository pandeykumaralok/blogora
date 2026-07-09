FROM ubuntu:22.04

LABEL org.opencontainers.image.title="blogora-image" \
      org.opencontainers.image.description="Webapp based on Ubuntu 22.04" \
      org.opencontainers.image.authors="Alok Kumar Pandey" \
      org.opencontainers.image.vendor="DevWithAlok" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="GNU"

# Build arguments (can be overridden during docker build)
ARG USERNAME=blogora
ARG UID=1000
ARG GID=1000

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHON_VERSION=3.12.10

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    zip \
    tar \
    git \
    vim \
    nano \
    build-essential \
    software-properties-common \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd / && \
    rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz

RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip3.12 /usr/bin/pip3

WORKDIR /app

COPY backend/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd --create-home --uid ${UID} --gid ${GID} --shell /bin/bash ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} /app

USER ${USERNAME}
