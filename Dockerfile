# vim:set ft=dockerfile:
FROM pcic/geospatial-python:gdal3
MAINTAINER https://github.com/pacificclimate/sandpiper
LABEL Description="sandpiper WPS" Vendor="pacificclimate" Version="1.7.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"
ENV THREDDS_URL_ROOT="https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets"

# Update system
RUN apk upgrade --update && \
  apk add \
  libxml2-dev \
  libxslt-dev \
  linux-headers \
  # R/Rpy2 dependencies (for wps-tools)
  # based on https://hub.docker.com/r/achillesrasquinha/rpy2/dockerfile
  gcc \
  gfortran \
  g++ \
  make \
  readline-dev \
  icu-dev \
  bzip2-dev \
  xz-dev \
  pcre-dev \
  libjpeg-turbo-dev \
  libpng-dev \
  tiff-dev  \
  curl-dev \
  zip \
  file \
  coreutils \
  musl-dev \
  libffi-dev \
  python3-dev \
  py3-pip \
  bash

# R build dependencies
# based on https://hub.docker.com/r/achillesrasquinha/rpy2/dockerfile
ENV BUILD_DEPS \
    cairo-dev \
    libxmu-dev \
    openjdk8-jre-base \
    pango-dev \
    perl \
    tiff-dev \
    tk-dev \
    libffi-dev

RUN apk add --virtual .build-deps $BUILD_DEPS && \
    apk add R R-dev && \
    apk del .build-deps

COPY . /opt/wps

WORKDIR /opt/wps

# Install WPS
RUN pip install --upgrade pip && \
    pip install sphinx psutil && \
    pip install -e . --ignore-installed && \
    pip install gunicorn

# Start WPS service on port 5000 on 0.0.0.0
EXPOSE 5000
CMD gunicorn --bind=0.0.0.0:5000 --timeout 150 sandpiper.wsgi:application

# docker build -t pcic/sandpiper .
# docker run -p 5000:5000 pcic/sandpiper
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
