FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive

# Install required packages
RUN apt-get -y update &&  \
    apt-get install -y apt-utils \
    python3 \
    g++ \
    make \
    cmake \
    libglu1-mesa-dev \
    freeglut3-dev \
    mesa-common-dev \
    git \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    mesa-utils

# Setup file system
WORKDIR /hypercube
ADD . .

# Running test files
ENTRYPOINT /bin/bash
