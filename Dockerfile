FROM python:3.9.7-slim

# Create the working directory
WORKDIR /bot

# Set necessary environment variables
ENV PIP_NO_CACHE_DIR=false

# Set the start command
ENTRYPOINT ["python"]
CMD ["-m" , "bot"]

# Install the latest version of poetry
RUN pip install -U poetry

# Install production dependencies using poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-root

# Copy the source code in last to optimize rebuilding the image
COPY . .
