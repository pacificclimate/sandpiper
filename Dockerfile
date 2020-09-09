FROM pcic/geospatial-python:gdal3

MAINTAINER https://github.com/pacificclimate/sandpiper
LABEL Description="sandpiper WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

WORKDIR /code

COPY requirements.txt ./

RUN apk add libxml2-dev libxslt-dev && \
    pip3 install sphinx && \
    pip3 install -r requirements.txt && \
    pip3 install gunicorn && \
    # These lines combat a vulnerability in pyxdg in both python2 and python3
    # https://github.com/advisories/GHSA-r6v3-hpxj-r8rv
    apt -y remove python-xdg \
      python3-xdg


COPY . .

EXPOSE 5003

CMD ["gunicorn", "--bind=0.0.0.0:5003", "sandpiper.wsgi:application"]

# docker build -t pcic/sandpiper .
# docker run -p 5003:5003 pcic/sandpiper
# http://localhost:5003/wps?request=GetCapabilities&service=WPS
# http://localhost:5003/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
