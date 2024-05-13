#!/bin/bash

if [[ "$1" =~ ^3.8.* ]]; then
    PYVER="3.8.19"
    DEBIANVER="bookworm"
    PREBUILT_PKG="client_se.cpython-38-x86_64-linux-gnu.so"
elif [[ "$1" =~ ^3.11.* ]]; then
    PYVER="3.11.9"
    DEBIANVER="bookworm"
    PREBUILT_PKG="client_se.cpython-311-x86_64-linux-gnu.so"
fi

echo $PYVER
echo $DEBIANVER
echo $PREBUILT_PKG

docker build -t cordatus-camera-player-agent:v1.0-x86-py$PYVER --build-arg PYVER=$PYVER --build-arg DEBIANVER=$DEBIANVER --build-arg PREBUILT_PKG=$PREBUILT_PKG .