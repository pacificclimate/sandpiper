# vim:set ft=dockerfile:
FROM continuumio/miniconda3
MAINTAINER https://github.com/nikola-rados/sandpiper
LABEL Description="sandpiper WPS" Vendor="Birdhouse" Version="0.1.0"

# Update Debian system
RUN apt-get update && apt-get install -y \
 build-essential \
&& rm -rf /var/lib/apt/lists/*

# Update conda
RUN conda update -n base conda

# Copy WPS project
COPY . /opt/wps

WORKDIR /opt/wps

# Create conda environment with PyWPS
RUN ["conda", "env", "create", "-n", "wps", "-f", "environment.yml"]

# Install WPS
RUN ["/bin/bash", "-c", "source activate wps && python setup.py install"]

# Start WPS service on port 5003 on 0.0.0.0
EXPOSE 5003
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["source activate wps && exec sandpiper start -b 0.0.0.0 -c /opt/wps/etc/demo.cfg"]

# docker build -t nikola-rados/sandpiper .
# docker run -p 5003:5003 nikola-rados/sandpiper
# http://localhost:5003/wps?request=GetCapabilities&service=WPS
# http://localhost:5003/wps?request=DescribeProcess&service=WPS&identifier=all&version=1.0.0
