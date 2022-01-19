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
Create a `.env` file with following contents:

   ```text
    TOKEN = <Your token> # See Discord Setup above
    PREFIX = "!" # the prefix the bot should use, will default to "!" if this is not present
   
    # Optional
    CHANNEL_DEVLOG=""
    CHANNEL_DEV_GURKBOT=""
    CHANNEL_DEV_REAGURK=""
    CHANNEL_DEV_GURKLANG=""
    CHANNEL_DEV_BRANDING=""
    CHANNEL_LOG=""

    EMOJI_TRASHCAN=""

    ROLE_STEERING_COUNCIL=""
    ROLE_MODERATORS=""
   ```

## Docker setup (recommended)
### Prerequisites
- Docker
- Docker-compose


### Running with Docker
1. pre-requisites: Docker
2. Install docker-compose: `pip install docker-compose`
3. Running and stopping the project
   ```sh
   # Build image and start project
   docker-compose up --build
  
   # Start project
   # use -d flag for detached mode
   docker-compose up
   
   # Stop project
   # Use ctrl+C if not in detached mode
   docker-compose stop
   
   # Delete containers
   # Use -v or --volumes flag to remove volumes
   docker-compose down
   ```
  
## Running manually (without docker)
### Prerequisites
- Python 3.9
- [Poetry](https://python-poetry.org/docs/#installation)

1. Add `DATABASE_URL` variable to `.env` file.

3. Command to run the bot: `poetry run task bot`
4. Commands to remember:
    ```
    poetry run task precommit - Installs the pre-commit git hook

    poetry run task format - Formats the project with black

    poetry run task lint- Runs pre-commit across the project, formatting and linting files.

    poetry run task bot - Runs the discord bot.
    ```

