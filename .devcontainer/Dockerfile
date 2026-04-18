# .devcontainer/Dockerfile
FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential git scons python3 python3-dev python3-pip \
      libprotobuf-dev protobuf-compiler libgoogle-perftools-dev \
      zlib1g-dev m4 pkg-config wget curl ca-certificates sudo \
      gcc-riscv64-linux-gnu gcc-aarch64-linux-gnu \
      telnet less vim nano \
 && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/student && \
    mkdir -p /home/student/work && chown -R student:student /home/student

# --- Build gem5 (this is the slow part — 10-30 min on first run) ---
ARG GEM5_TAG=v23.0.1.0
RUN git clone --depth 1 --branch ${GEM5_TAG} https://github.com/gem5/gem5.git /opt/gem5-src && \
    cd /opt/gem5-src && \
    scons build/RISCV/gem5.opt -j"$(nproc)" && \
    mkdir -p /opt/gem5/bin && cp build/RISCV/gem5.opt /opt/gem5/bin/gem5-riscv && \
    cp -r configs /opt/gem5/ && \
    rm -rf /opt/gem5-src

ENV PATH=/opt/gem5/bin:$PATH

USER student
WORKDIR /home/student/work
