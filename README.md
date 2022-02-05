# Gurkbot

The official bot for [the Gurkult](https://gurkult.com/discord) — an open source community with the aim of bringing people together.

---

## Contribute

If you want to contribute, report a problem, add or suggest a new fix or feature, you can [open a new issue](https://github.com/gurkult/gurkbot/issues/new/choose). The issue should be accepted and discussed before starting to work on the feature. See [Dev Installation](#Dev-Installation) to know how to start working on said feature.

---

## Discord Setup

To get a **token**, go to [Discord Developer Portal](https://discord.com/developers/applications). Create an application and add a bot.

## Dev Installation
1. Clone the repository:
- Traditional way: `git clone https://github.com/gurkult/gurkbot.git` or `git clone git@github.com:gurkult/gurkbot.git`.

- Using Github CLI: `gh repo clone gurkult/gurkbot`.

Then navigate to the directory `cd gurkbot/`

2. Create a new branch by `git checkout -b <name of new local branch> main` or `git switch -c <name of new local branch> main`. Make sure the new branch name is related to the feature or the fix you have in mind.


## Environment variable setup
Create a `.env` file in the project root folder.
Copy the contents from [`.env-example`](https://github.com/gurkult/gurkbot/blob/main/.env-example) file into your `.env` file and fill up the fields with your bot token and server details.


## Docker setup (recommended)

1. Pre-requisites
    - [Docker](https://docs.docker.com/engine/install/)
    - [Docker Compose](https://docs.docker.com/compose/install/)
4. Running and stopping the project
    ```SH
    # Build image and start project
    # This will start both the Postgres database and the bot.
    # Running this the first time will build the image.
    docker-compose up --build

    # Start/create the postgres database and the bot containers.
    docker-compose up

    # Use -d flag for detached mode
    # This will free the terminal for other uses.
    docker-compose up -d

    # Stop project
    # Use ctrl+C if not in detached mode
    docker-compose stop

    # Stop and remove containers.
    docker-compose down

    # Use -v or --volumes flag to remove volumes
    docker-compose down --volumes

    # Alternativily, `docker-compose` can be
    # replaced with `docker compose` (without the hyphen).
    ```
5. Running only database with docker
    ```SH
    docker-compose up postgres
    ```

5. Running only bot with docker
    ```SH
    docker-compose up gurkbot --no-deps
    ```


## Running manually (without docker)
1. Prerequisites
    - [Python 3.9](https://www.python.org/downloads/)
    - [Poetry](https://python-poetry.org/docs/#installation)
    - Postgres database
        - [Download](https://www.postgresql.org/download/)

2. Database setup
    - Open terminal/cmd and enter psql
    ```SH
    psql -U postgres -d postgres
    ```
    - Create user and database
    ```SH
    CREATE USER gurkbotdb WITH SUPERUSER PASSWORD 'gurkbotdb';
    CREATE DATABASE gurkbot WITH OWNER gurkbotdb;
    ```
3. Add `DATABASE_URL` variable to `.env` file.
    ```
    DATABASE_URL = postgres://gurkbotdb:gurkbotdb@localhost:5432/gurkbot
    ```
    #### About the URL
    - format: `postgres://<username>:<password>@<host>:<port>/<database>`
    - If you have changed any of the parameters such has `port`, `username`, `password` or `database` during installation or in psql, reflect those changes in the `DATABASE_URL`.
    - The host will be `localhost` unless you want to connect to a database which is not hosted on your machine.

4. Command to run the bot: `poetry run task bot`
5. Commands to remember:
    ```SH
    # Installs the pre-commit git hook.
    poetry run task precommit

    # Formats the project with black.
    poetry run task format

    # Runs pre-commit across the project, formatting and linting files.
    poetry run task lint

    # Runs the discord bot.
    poetry run task bot
    ```
