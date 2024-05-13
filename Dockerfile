ARG PYVER=python.version
ARG DEBIANVER=os.version
ARG PREBUILT_PKG=package.version

FROM python:${PYVER}-${DEBIANVER}

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /cse-camera-agent

COPY packages/${PREBUILT_PKG} /cse-camera-agent/${PREBUILT_PKG}
COPY requirements.txt /cse-camera-agent/requirements.txt
COPY camera_player.py /cse-camera-agent/camera_player.py

RUN pip3 install -r requirements.txt && \
    rm -rf /root/.cache

CMD [ "/bin/bash" ]