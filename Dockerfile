FROM python:3.8-slim

# Create the working directory
WORKDIR /bot

# Install pipenv
RUN pip install -U poetry

# Install dependencies using poetry
COPY poetry.lock poetry.toml pyproject.toml ./
RUN poetry install --no-dev

# Copy the source code in last to optimize rebuilding the image
COPY . .

# Set the start command
ENTRYPOINT ["poetry"]
CMD ["run", "bot"]
