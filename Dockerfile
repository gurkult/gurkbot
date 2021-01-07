FROM python:3.8-slim

# Create the working directory
WORKDIR /bot

# Set pip to have cleaner logs and no saved cache
ENV PIP_NO_CACHE_DIR=false \
    PIPENV_HIDE_EMOJIS=1 \
    PIPENV_IGNORE_VIRTUALENVS=1 \
    PIPENV_NOSPIN=1

# Set the start command
ENTRYPOINT ["python3"]
CMD ["-m", "bot"]

# Install pipenv
RUN pip install -U pipenv

# Install project dependencies
COPY Pipfile* ./
RUN pipenv install --system --deploy

# Copy the source code in last to optimize rebuilding the image
COPY . .
