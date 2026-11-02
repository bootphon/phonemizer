# Use this file to build a docker image of phonemizer (using festival,
# espeak-ng and mbrola from the ubuntu repo):
#
#    sudo docker build -t phonemizer .
#
# Then open a bash session in docker with:
#
#    sudo docker run -it phonemizer /bin/bash
#
# You can then use phonemizer within docker. See the docker doc for
# advanced usage.


# Use an official Ubuntu as a parent image, its python must be supported by
# phonemizer (python>=3.10)
FROM ubuntu:24.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# set the working directory to /phonemizer
WORKDIR /phonemizer

# install dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        festival \
        festvox-us1 \
        festlex-cmu \
        festlex-poslex \
        espeak-ng \
        mbrola \
        mbrola-fr1 \
        python3 \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# the system python does not accept packages installed with pip (PEP 668), so
# phonemizer is installed in a virtual environment, made the default python
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=/opt/venv/bin:$PATH
RUN python3 -m venv /opt/venv

# copy the phonemizer code within the docker image
COPY . /phonemizer

# install phonemizer and run the tests
RUN pip install --no-cache-dir .[test,segments] && \
    phonemize --version && \
    pytest -v test
