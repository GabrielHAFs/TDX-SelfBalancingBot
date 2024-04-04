# For arm64v8 use:
ARG IMAGE_ARCH=linux/arm64/v8
ARG IMAGE_TAG=bookworm-slim
# ARG DEBIAN_SNAPSHOT=20210408T000000Z
ARG TORADEX_SNAPSHOT=20210909T072507Z
ARG USE_TORADEX_SNAPSHOT=1
ARG ADD_TORADEX_REPOSITORY=1
FROM --platform=$IMAGE_ARCH debian:$IMAGE_TAG AS base

RUN apt-get update && apt-get install -y nano build-essential wget python3 python3-serial kmod python3-websockets && rm -rf /var/lib/apt/lists/*

# Download and compile devmem2
WORKDIR /tmp
RUN wget http://free-electrons.com/pub/mirror/devmem2.c && \
    gcc -o devmem2 devmem2.c && \
    mv devmem2 /usr/local/bin

COPY aclient.py /app/aclient.py

WORKDIR /app

COPY script.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/script.sh

CMD ["/usr/local/bin/script.sh"]