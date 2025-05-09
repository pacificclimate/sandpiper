FROM pcic/geospatial-python:3.4.0

LABEL Maintainer="https://github.com/pacificclimate/sandpiper" \
  Description="sandpiper WPS" \
  Vendor="pacificclimate" \
  Version="1.7.1"
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"
ENV THREDDS_URL_ROOT="https://marble-dev01.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets"

# Update system
RUN apk upgrade --update && \
  apk add \
  libxml2-dev \
  libxslt-dev \
  linux-headers\
  curl

WORKDIR /tmp
COPY pyproject.toml poetry.lock* ./

RUN curl -sSL https://install.python-poetry.org | python3
RUN pip install --upgrade pip && \
  pip install poetry && \
  poetry config virtualenvs.create false
RUN poetry install

COPY . .
# Start WPS service on port 5000 on 0.0.0.0
EXPOSE 5000
CMD ["gunicorn", "--bind=0.0.0.0:5000", "--timeout", "150", "sandpiper.wsgi:application"]

# docker build -t pcic/sandpiper .
# docker run -p 5000:5000 pcic/sandpiper
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0