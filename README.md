# Gurkbot

The official bot for [**THE GURKULT OPEN SOURCE COMMUNITY - DISCORD SERVER**](https://bit.ly/Gurkult-Discord).

---

## Discord Setup

To get a **token**, go to [Discord Developer Portal](https://discord.com/developers/applications). Create an application and add a bot.

## Dev Installation

1. Traditional way: `git clone <url>`.
   Using Github CLI: `gh repo clone gurkult/gurkbot`. Then navigate to the directory `cd gurkbot/`
2. Create a new branch by `git branch -b <name of new branch> main` or `git switch -c <name of new branch>`.

3. Create a `.env` file with following contents:

   ```text
   TOKEN = <Your token> # See Discord Setup above
   PREFIX = "!" # the prefix the bot should use, will default to "!" if this is not present

   ```

4. Install pipenv: `pip install pipenv` and run the following:

   ```sh
   # This will install the development and project dependencies.
   pipenv sync --dev

   # This will install the pre-commit hooks.
   pipenv run pre-commit install

   # Optionally: run pre-commit hooks to initialize them.
   pipenv run pre-commit run --all-files

   # Enter pipenv shell.
   pipenv shell

   # Run the bot
   pipenv run python -m bot

   ```
