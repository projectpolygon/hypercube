FROM ubuntu

# Install required packages
RUN apt-get update -y && \
    apt-get install -y apt-utils && \
    apt-get install -y python3 && \
    apt-get install -y g++ && \
    apt-get install -y make && \
    apt-get install -y cmake && \
    apt-get install -y libglu1-mesa-dev freeglut3-dev mesa-common-dev && \
    apt-get install -y git && \
    apt-get install -y libxrandr-dev && \
    apt-get install -y libxinerama-dev && \
    apt-get install -y libxcursor-dev && \
    apt-get install -y libxi-dev &&  \
    apt-get install -y mesa-utils && \
    mkdir hypercube

# Setup file system
ADD . /hypercube
WORKDIR /hypercube

# Running test files
ENTRYPOINT /bin/bash
