# Gurkbot

The official bot for [**THE GURKULT OPEN SOURCE COMMUNITY - DISCORD SERVER**](https://bit.ly/Gurkult-Discord).

---

## Contribute

If you want to contribute, report a problem, add or suggest a new fix or feature, you can either [open a new issue](https://github.com/gurkult/gurkbot/issues/new/choose) or [open a new pull request](https://github.com/gurkult/gurkbot/compare). For those who want to contribute, see [Dev Installation](#Dev-Installation).

---

## Discord Setup

To get a **token**, go to [Discord Developer Portal](https://discord.com/developers/applications). Create an application and add a bot.

## Dev Installation

1. Traditional way: `git clone <url>`.
   Using Github CLI: `gh repo clone gurkult/gurkbot`. Then navigate to the directory `cd gurkbot/`
2. Create a new branch by `git branch -b <name of new local branch> main` or `git switch -c <name of new local branch> main`. Make sure the new branch name is related to the feature or the fix you have in mind.

3. Create a `.env` file with following contents:

   ```text
   TOKEN = <Your token> # See Discord Setup above
   PREFIX = "!" # the prefix the bot should use, will default to "!" if this is not present

4. Install pipenv: `pip install pipenv` and run the following:

   ```sh
   # This will install the development and project dependencies.
   pipenv sync --dev

   # This will install the pre-commit hooks.
   pipenv run precommit

   # Optionally: run pre-commit hooks to initialize them.
   pipenv run lint
   
   # Run the bot
   pipenv run start

   ```
5. Lint and format your code properly (use black or flake8), and push changes `git push -u origin <name of new remote branch>`
