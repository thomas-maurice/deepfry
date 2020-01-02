FROM ubuntu:latest
RUN apt-get update && apt-get upgrade -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        ca-certificates \
        libopencv-dev \
        libopencv-imgcodecs3.2 \
        libopencv-imgproc3.2 \
        libopencv-ml3.2 \
        libopencv-objdetect3.2 \
        libopencv-imgcodecs-dev \
        libopencv-imgproc-dev \
        libopencv-ml-dev \
        libopencv-objdetect-dev \
        libopencv-video-dev \
        libopencv-video3.2 \
        libopencv-videoio-dev \
        libopencv-videoio3.2 \
        libopencv-viz-dev \
        libopencv-viz3.2 \
        python3-dev \
        python3-pip \
        libv4l-dev \
        cmake \
        libpng-dev \
        libtiff-dev && \
        apt-get clean && \
        apt-get autoclean && \
        rm -rf /var/cache/apt
RUN useradd -m -d /var/lib/deepfry -s /bin/bash deepfry
COPY deepfry.py requirements.txt /var/lib/deepfry/
RUN pip3 install -r /var/lib/deepfry/requirements.txt &&  rm -rf ~/.cache/pip
COPY filters /var/lib/deepfry/filters
USER deepfry
WORKDIR /var/lib/deepfry
# If you don't do the 2 last one click is going to fuck up for some reason
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
