# syntax=docker/dockerfile:1.7

############################
# Stage 1: build gem5 from source
############################
FROM ubuntu:22.04 AS gem5-build

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential git scons python3-dev python3-pip            \
        zlib1g-dev libprotobuf-dev protobuf-compiler libprotoc-dev   \
        libgoogle-perftools-dev m4 libboost-all-dev pkg-config       \
        libpng-dev libhdf5-serial-dev libelf-dev                     \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
ARG GEM5_TAG=v23.0.1.0
RUN git clone --depth 1 --branch ${GEM5_TAG} https://github.com/gem5/gem5.git
WORKDIR /src/gem5

# Build three ISAs. -j$(nproc) is fast but RAM-hungry; use -j2 if OOM-killed.
# BuildKit cache mount keeps SCons object files between rebuilds.
RUN --mount=type=cache,target=/src/gem5/build,id=gem5-build \
    scons build/X86/gem5.opt   -j"$(nproc)" && \
    scons build/ARM/gem5.opt   -j"$(nproc)" && \
    scons build/RISCV/gem5.opt -j"$(nproc)" && \
    cp build/X86/gem5.opt   /opt/gem5-x86 && \
    cp build/ARM/gem5.opt   /opt/gem5-arm && \
    cp build/RISCV/gem5.opt /opt/gem5-riscv

############################
# Stage 2: lean runtime image
############################
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PATH=/opt/gem5/bin:$PATH       \
    GEM5_RESOURCE_DIR=/opt/gem5-resources

# Runtime-only dependencies (no compiler, no source).
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip                                       \
        libprotobuf23 libgoogle-perftools4 libhdf5-103 libpng16-16 \
        gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu          \
        wget curl ca-certificates sudo nano less file unzip xz-utils \
        make telnet git \
    && rm -rf /var/lib/apt/lists/*

# Python deps for gem5 stdlib (resource download, plotting).
RUN pip3 install --no-cache-dir \
        m5 \
        matplotlib pandas

# Copy gem5 binaries + the configs/ tree from the build stage.
RUN mkdir -p /opt/gem5/bin
COPY --from=gem5-build /opt/gem5-x86   /opt/gem5/bin/gem5-x86
COPY --from=gem5-build /opt/gem5-arm   /opt/gem5/bin/gem5-arm
COPY --from=gem5-build /opt/gem5-riscv /opt/gem5/bin/gem5-riscv
COPY --from=gem5-build /src/gem5/configs /opt/gem5/configs

# Lab content + helpers.
COPY labs/  /labs/
COPY lab    /usr/local/bin/lab
RUN chmod +x /usr/local/bin/lab

# Non-root user.
RUN useradd -m -s /bin/bash -G sudo student && \
    echo "student ALL=(ALL) NOPASSWD:ALL" >/etc/sudoers.d/student && \
    mkdir -p /home/student/work && chown student:student /home/student/work
USER student
WORKDIR /home/student/work

# gem5 prints what port to telnet into; expose a generous range.
EXPOSE 3456-3460
CMD ["bash"]
