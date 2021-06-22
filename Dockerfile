FROM python:3.8-slim

# Create the working directory
WORKDIR /bot

# Install the latest version of poetry
RUN pip install -U poetry

# Install production dependencies using poetry
COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-root

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Set the start command
ENTRYPOINT ["python"]
CMD ["-m" , "bot"]
