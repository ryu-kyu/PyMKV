FROM ubuntu:latest

# Setup to add package repo and install python3.11
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

# Install Python 3.11 and pip
RUN apt-get update && \
    apt-get install -y python3.11 python3-pip

# Install Poetry from Git
RUN curl -sSL https://install.python-poetry.org | python3 - --git https://github.com/python-poetry/poetry.git@main
# Add Poetry to PATH
ENV PATH="$HOME/.local/bin:$PATH"

# Docker is already isolated, so turn venv off 
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /workspace

# Install project dependencies using Poetry
RUN poetry install

# Set the entrypoint command
CMD ["sleep", "infinity"]