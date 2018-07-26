# Use this file to build a docker image of phonemizer (using
# festival-2.5 and espeak-ng-1.49.2):
#
#    sudo docker build -t phonemizer .
#
# Then open a bash session in docker with:
#
#    sudo docker run -it phonemizer /bin/bash
#
# You can then use wordseg within docker. See the docker doc for
# advanced usage.


# Use an official Ubuntu as a parent image
FROM ubuntu:18.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

# Set the working directory to /phonemizer
WORKDIR /phonemizer

RUN apt-get update && apt-get upgrade -y


## festival-2.5
RUN apt-get install -y festival


## espeak-ng

# install dependancies for espeak-ng
RUN apt-get install -y make autoconf automake libtool pkg-config gcc wget unzip

# download the source code for espeak-ng-1.49.2
RUN wget https://github.com/espeak-ng/espeak-ng/releases/download/1.49.2/espeak-ng-1.49.2.tar.gz && \
    tar xf espeak-ng-1.49.2.tar.gz && \
    mv espeak-ng-1.49.2 espeak-ng && \
    rm -f espeak-ng-1.49.2.tar.gz

# get extended espeak-ng dictionnary for Cantonese
RUN wget http://espeak.sourceforge.net/data/zh_listx.zip && \
    unzip zh_listx.zip -d espeak-ng/espeak-ng-data && \
    rm -f zh_listx.zip

# get extended espeak-ng dictionnary for Mandarin
RUN wget http://espeak.sourceforge.net/data/zhy_list.zip && \
    unzip zhy_list.zip -d espeak-ng/espeak-ng-data && \
    rm -f zhy_list.zip

# get extended espeak-ng dictionnary for Russian
RUN wget http://espeak.sourceforge.net/data/ru_listx.zip && \
    unzip ru_listx.zip -d espeak-ng/espeak-ng-data && \
    rm -f ru_listx.zip

# configure, compile and install espeak-ng
RUN cd espeak-ng && \
    ./autogen.sh && \
    ./configure --with-extdict-ru --with-extdict-zh --with-extdict-zhy && \
    make && \
    make LIBDIR=/usr/lib/x86_64-linux-gnu install


## phonemizer

# install dependancies for phonemizer
RUN apt-get install -y git python3 python3-pip python3-pytest

# install phonemizer
RUN git clone https://github.com/bootphon/phonemizer.git && \
    cd phonemizer && \
    python3 setup.py install

# test the phonemizer
RUN phonemize --version && \
    python3 -m pytest -v phonemizer/test
