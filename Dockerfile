FROM pcic/geospatial-python

MAINTAINER https://github.com/pacificclimate/sandpiper
LABEL Description="sandpiper WPS" Vendor="pacificclimate" Version="0.1.0"

ENV PIP_INDEX_URL="https://pypi.pacificclimate.org/simple/"

WORKDIR /code

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install sphinx && \
    pip install -r requirements.txt && \
    pip install gunicorn

COPY . .

EXPOSE 5002

CMD ["gunicorn", "--bind=0.0.0.0:5003", "sandpiper.wsgi:application"]

# docker build -t pacificclimate/sandpiper .
# docker run -p 5003:5003 pacificclimate/sandpiper
# http://localhost:5003/wps?request=GetCapabilities&service=WPS
# http://localhost:5003/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
