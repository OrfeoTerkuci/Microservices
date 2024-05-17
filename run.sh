#! /bin/bash

trap 'echo "Caught signal, exiting..."; exit 1' SIGINT SIGTERM


pull_images() {
    echo "Pulling images..."
    podman pull python:3.12-rc-slim-buster
}

run_podman_compose() {
    echo "Running podman compose..."
    podman compose up
}

pull_images
run_podman_compose