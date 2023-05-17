# Dockerfile has three Arguments: base, tag
# base - base image (default: ubuntu, optional: debian)
# tag - tag for base mage (default: 22.04, optional: stable-slim)
#
# To build the image run from the root of the repository:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> --build-arg arg=value -f docker/Dockerfile
# or using default args:
# $ docker build -t <dockerhub_user>/<dockerhub_repo> -f docker/Dockerfile
#
# To run (ENTRYPOINT is used) it is required to provide on what address API is running! e.g.:
# docker run -d -p 3000:3000 ai4eosc/deep-oc-gui_rnacontactmap --api_url=http://193.196.37.98:5000/

# set the base image. default is debian, optional ubuntu
ARG base=ubuntu
# set the tag (e.g. 20.04, latest, stable, stable-slim (for debian) )
ARG tag=20.04

# Base image, e.g. debian:stable or ubuntu:bionic
FROM ${base}:${tag}

LABEL maintainer='F.Alibabaei, V.Kozlov (KIT)'
# GUI for rnacontactmap based on gradio.app

# Install system updates and tools
ENV DEBIAN_FRONTEND=noninteractive

# use TIME arg to force rebuild from this step
ARG api_date=none
RUN echo ${api_date} && apt-get update && apt-get install -y --no-install-recommends \
# Install system updates and tools
#        git \
        nano \
#        procps \
#        gcc \
#        python3-dev \
        python3-setuptools \
        python3-pip && \
#        python3-wheel && \
# Clean up & back to dialog front end
    apt-get autoremove -y && \
    apt-get clean -y && \
    rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND=dialog

# Install user app:
COPY *.py /app/
COPY requirements.txt /app
RUN cd /app && pip3 install --no-cache-dir -r requirements.txt
WORKDIR /app

# change to non-root user
RUN useradd -m user
RUN chown -R user:user /app
USER user

# Set environments
ENV LANG C.UTF-8

EXPOSE 3000
# Start the app
ENTRYPOINT ["python3", "./launch.py", "--ui_port", "3000"]
