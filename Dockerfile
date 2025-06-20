FROM pcic/geospatial-python:3.8.4

LABEL Maintainer="https://github.com/pacificclimate/sandpiper" \
  Description="sandpiper WPS" \
  Vendor="pacificclimate" \
  Version="1.7.1"
ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"
ENV THREDDS_URL_ROOT="https://marble-dev01.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets"

# Update system
RUN apt-get update && apt-get upgrade -y && \
  apt-get install -y \
  libxml2-dev \
  libxslt-dev \
  wget


WORKDIR /tmp

ENV POETRY_HOME="/opt/poetry"
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && \
  apt-get install -y --no-install-recommends python3-pip curl  && \
  curl -sSL https://install.python-poetry.org | python3

COPY . .

RUN poetry config virtualenvs.in-project true && \
  poetry install

# Start WPS service on port 5000 on 0.0.0.0
EXPOSE 5000
CMD ["poetry", "run","gunicorn", "--bind=0.0.0.0:5000", "--timeout", "150", "sandpiper.wsgi:application"]

# docker build -t pcic/sandpiper .
# docker run -p 5000:5000 pcic/sandpiper
# http://localhost:5000/wps?request=GetCapabilities&service=WPS
# http://localhost:5000/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0