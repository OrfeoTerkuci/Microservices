#! /bin/bash

cleanup() {
    echo "Cleaning up..."
    podman compose down --remove-orphans
}

trap 'echo "Caught signal, exiting..."; cleanup; exit 1' SIGINT SIGTERM
trap cleanup EXIT

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