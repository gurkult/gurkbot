# Setup Instructions

1. [Install requirements](#Requirements)
2. [Setup a test server and a bot account](#Test-Server-and-Bot-Account)
3. [Fork the project repository](#Fork-the-Project)
4. [Configure the development environment](#Development-Environment)
5. [Run the project](#Run-The-Project)
6. [Work with git to make changes](#Working-with-Git)

## Requirements

- [Python 3.8](https://docs.python.org/3.8/)
- [Pipenv](https://pipenv.pypa.io/en/latest/basics/)
- [Git](https://git-scm.com/doc)

## Test Server and Bot Account

You will need your own test server and bot account on Discord to test your changes to the bot.

1. Create a test server.
2. Create a bot account and invite it to the server you just created.
3. Create the following text channels:
   \#dev-log

Note down the IDs for your server, as well as any channels and roles created.
Learn how to obtain the ID of a server, channel or role **[here](https://pythondiscord.com/pages/contributing/setting-test-server-and-bot-account/#setting-up-a-test-server).**

## Fork the Project

You will need your own remote (online) copy of the project repository, known as a fork.

You will do all your work in the fork rather than directly in the main repository.

# Development Environment

##### Once You Have Your Fork, You Will Need To Clone The Repository To Your Computer.

```shell
$ git clone https://github.com/<your username>/gurkbot
...
$ cd gurkbot
```
**or using the github CLI**
```shell
$ gh repo clone <your username>/gurkbot
...
$ cd gurkbot
```


##### After cloning, proceed to install the project's dependencies.

Make sure you are in the project directory.

```shell
# This will install the development and project dependencies.
pipenv sync --dev

# This will install the pre-commit hooks.
pipenv run precommit

# Optionally: run pre-commit hooks to initialize them.
pipenv run lint
```

##### After installing dependencies, you will have to setup environment variables:After installing dependencies, you will have to setup environment variables:

1. Create a text file named .env in your project root (that's the base folder of your repository):

Note: The entire file name is literally .env

3. Open the file with any text editor.
4. Each environment variable is on its own line, with the variable and the value separated by a = sign.

## The following variables are needed for running Gurkbot:

| ENV VARIABLE NAME | WHAT IS IT?                                                               |
| ----------------- | ------------------------------------------------------------------------- |
| TOKEN             | Bot Token from the Discord developer portal                               |
| PREFIX            | The prefix the bot should use, will default to "!" if this is not present |
| CHANNEL_DEVLOG    | ID of the #dev-log channel                                                |


## Run The Project

To run the project, use the pipenv command pipenv run start in the project root.

```shell
$ pipenv run start
```

## Working with Git

Now that you have everything setup, it is finally time to make changes to the bot! If you have not yet read the contributing guidelines, now is a good time. Contributions that do not adhere to the guidelines may be rejected.

Notably, version control of our projects is done using Git and Github. It can be intimidating at first, so feel free to ask for any help in the server.

Click [here](https://pythondiscord.com/pages/contributing/working-with-git/ "here") to see the basic Git workflow when contributing to one of our projects


# Rules

1. You must be a member of [our Discord community](https://discord.gg/W9DSfryp8Y) in order to contribute to this project.

2. Your pull request must solve an issue created or approved by a staff member. These will be labelled with the `approved` label. Feel free to suggest issues of your own, which staff can review for approval.

3. **No force-pushes** or modifying the Git history in any way.

4. If you have direct access to the repository, **create a branch for your changes** and create a pull request for that branch. If not, create a branch on a fork of the repository and create a pull request from there.
    * If PRing from your own fork, **ensure that "Allow edits from maintainers" is checked**. This gives permission for maintainers to commit changes directly to your fork, speeding up the review process.
    
5. **Adhere to the prevailing code style**, which we enforce using [`flake8`](http://flake8.pycqa.org/en/latest/index.html) and [`pre-commit`](https://pre-commit.com/).
    * Run `flake8` and `pre-commit` against your code **before** you push. Your commit will be rejected by the build server if it fails to lint. You can run the lint by executing `pipenv run lint` in your command line.
 
6. **Make great commits**. A well structured git log is key to a project's maintainability; it efficiently provides insight into when and *why* things were done for future maintainers of the project.
    * A more in-depth guide to writing great commit messages can be found in Chris Beam's [*How to Write a Git Commit Message*](https://chris.beams.io/posts/git-commit/).
    
7. If someone is working on an issue or pull request, **do not open your own pull request for the same task**. Instead, collaborate with the author(s) of the existing pull request. Duplicate PRs opened without communicating with the other author(s) or staff, will be closed. 
    * One option is to fork the other contributor's repository and submit your changes to their branch with your own pull request. We suggest following these guidelines when interacting with their repository as well.
