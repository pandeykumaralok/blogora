FROM ubuntu:22.04

LABEL org.opencontainers.image.title="blogora-image" \
      org.opencontainers.image.description="Blogora web application based on Ubuntu 22.04" \
      org.opencontainers.image.authors="Alok Kumar Pandey" \
      org.opencontainers.image.vendor="DevWithAlok" \
      org.opencontainers.image.version="1.0.0" \
      org.opencontainers.image.licenses="GPL-3.0"

#############################################
# Build Arguments
#############################################

ARG USERNAME=blogora
ARG UID=1000
ARG GID=1000

ENV DEBIAN_FRONTEND=noninteractive

#############################################
# Install Python 3.12 and OS Packages
#############################################

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        gnupg \
        gpg-agent \
        dirmngr \
        ca-certificates \
        wget \
        curl \
        unzip \
        zip \
        tar \
        git \
        vim \
        nano \
        awk \
        build-essential && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-dev \
        python3.12-venv && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#############################################
# Application
#############################################

WORKDIR /app

COPY backend/requirements.txt .

RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

#############################################
# Create Non-Root User
#############################################

RUN groupadd --gid ${GID} ${USERNAME} && \
    useradd \
        --uid ${UID} \
        --gid ${GID} \
        --create-home \
        --shell /bin/bash \
        ${USERNAME} && \
    chown -R ${USERNAME}:${USERNAME} /app

USER ${USERNAME}

CMD ["/bin/bash"]