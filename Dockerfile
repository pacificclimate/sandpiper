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
  linux-headers

COPY . /tmp
WORKDIR /tmp

# Install WPS
RUN pip install --upgrade pip && \
    pip install sphinx psutil && \
    pip install . --ignore-installed && \
    pip install gunicorn

# Start WPS service on port 5000 on 0.0.0.0
EXPOSE 5000
CMD gunicorn --bind=0.0.0.0:5000 --timeout 150 sandpiper.wsgi:application

# docker build -t pcic/sandpiper .
# docker run -p 5000:5000 pcic/sandpiper
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0