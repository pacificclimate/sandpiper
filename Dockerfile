# vim:set ft=dockerfile:
FROM pcic/geospatial-python:gdal3
MAINTAINER https://github.com/pacificclimate/sandpiper
LABEL Description="sandpiper WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"
ENV THREDDS_URL_ROOT="https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets"

# Update system
RUN apk add \
  libxml2-dev \
  libxslt-dev \
  linux-headers

COPY . /opt/wps

WORKDIR /opt/wps

# Create python environment
RUN ["python", "-m", "venv", "venv"]

# Install WPS
RUN ["sh", "-c", "source venv/bin/activate && pip install sphinx psutil && pip install -e ."]

# Start WPS service on port 5003 on 0.0.0.0
EXPOSE 5003
ENTRYPOINT ["sh", "-c"]
CMD ["source venv/bin/activate && exec sandpiper start -b 0.0.0.0"]

# docker build -t pcic/sandpiper .
# docker run -p 5003:5003 pcic/sandpiper
# http://localhost:5003/wps?request=GetCapabilities&service=WPS
# http://localhost:5003/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
