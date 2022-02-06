FROM ubuntu:18.04

ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install software-properties-common -y && \
    rm -rf /var/lib/apt/lists/*

RUN add-apt-repository ppa:ubuntugis/ppa -y && \
    add-apt-repository ppa:deadsnakes/ppa -y

RUN apt-get update \
    && apt-get update \
    && apt-get install python3-pip -y \
    && apt-get install wait-for-it -y \	
    && apt-get install -y --no-install-recommends \	
    python3.8 python3.8-dev python3.8-distutils python3-healpy libssl-dev \	
    libcurl4-openssl-dev python3-setuptools gcc curl git

COPY ./requirements.txt .
RUN python3.8 -m pip install -r requirements.txt

ADD . /app/
WORKDIR /app
