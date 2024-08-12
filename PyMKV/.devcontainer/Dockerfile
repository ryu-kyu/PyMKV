FROM python:3.11-slim

# Change shell to bash
SHELL ["/bin/bash", "-c"] 

# Setup to add package repo and install python3.11
RUN apt-get update && apt-get install -y software-properties-common

# Install Poetry from Git
RUN pip install poetry

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1
ENV PATH="$PATH:$POETRY_HOME/bin"

WORKDIR /workspace

# Set the entrypoint command
CMD ["sleep", "infinity"]