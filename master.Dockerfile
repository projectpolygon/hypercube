# ====== Base ======
FROM ubuntu:latest AS base
RUN apt -y update

# Required Packages
ENV DEBIAN_FRONTEND=noninteractive
RUN apt -y install \
    apt-utils \
    python3 \
    python3-pip
    # g++ \
    # make \
    # cmake \
    # libglu1-mesa-dev \
    # freeglut3-dev \
    # mesa-common-dev \
    # libxrandr-dev \
    # libxinerama-dev \
    # libxcursor-dev \
    # libxi-dev \
    # mesa-utils

# ====== Test Environment ======
FROM base as test-env
WORKDIR /hypercube/
COPY ./src .

# Install test dependencies
RUN pip3 install \
    -r tests/requirements.txt \
    # -r common/requirements.txt # no common specific requirements yet
    -r master/requirements.txt

# run common and master unit tests
RUN pytest tests/common_tests tests/master_tests


# ====== Master ======
FROM base as final
WORKDIR /hypercube
COPY --from=test-env /hypercube/common ./common
COPY --from=test-env /hypercube/master ./master

# Install python dependencies
RUN pip3 install \
    # -r common/requirements.txt # no common specific requirements yet
    -r master/requirements.txt

# Run master
ENTRYPOINT python3 -m master.master
