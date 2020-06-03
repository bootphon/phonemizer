# Use this file to build a docker image of phonemizer (using
# festival-2.5 and espeak-ng-1.49.2 from ubuntu repo):
#
#    sudo docker build -t phonemizer .
#
# Then open a bash session in docker with:
#
#    sudo docker run -it phonemizer /bin/bash
#
# You can then use phonemizer within docker. See the docker doc for
# advanced usage.


# Use an official Ubuntu as a parent image
FROM ubuntu:18.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Set the working directory to /phonemizer
WORKDIR /phonemizer

# install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        festival \
        espeak-ng \
        git \
        mbrola \
        mbrola-fr1 \
        python3 \
        python3-pip && \
    apt-get clean

# Pytest needs to be installed through pip to make sure we have a recent version
RUN pip3 install pytest pytest-cov

# Tests expect python to be available as executable 'python' not 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# install phonemizer and run the tests
RUN git clone https://github.com/bootphon/phonemizer.git && \
    cd phonemizer && \
    python3 setup.py install && \
    phonemize --version && \
    python3 -m pytest -v test
