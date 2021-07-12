# YAudit

This repository contains the source code for experiments auditing personalization on YouTube.

## Installation

Install packages using `pip3 install -r bot.requirements.txt`.

### Database migrations

Create databases for the environments that you want to use (e.g., `yaudit`).

Execute existing migrations on the databases using (update database URL):

```
alembic upgrade head
```

Auto-generating migrations:
```
alembic revision --autogenerate
```

### Selenium Bot

To run the selenium bot, packages need to be installed using `pip3 install -r bot-requirements.txt`

Alternatively, docker can be used to run the bot. A docker image can be build simply by running `docker build . -f bot.Dockerfile -t [NAME]` when located in the root directory.



## Usage


### Updating migrations

To create new migrations based on changes in Python model classes, use:

```
DATABASE_URL=postgresql://localhost/yaudit_dev python3 -m yaudit.manage db migrate
```

## Loading seed data

```
python3 -m scripts.seed_data
```

## Running selenium bot

To run the bot, some setup needs to performed first:

1. A postgres database must exist.
This potgres database must contain configuration and account information.

Example configuration looks like this:

```
name=Test
bubble_create_strategy='implicit'
bubble_burst_strategy='implicit'
params={"watch_duration": 1800, "sleep_time": 1200, "number_of_videos": 40, "query_frequency": 2, "reverse": "false"}
```

For account information, only the username and password is required.

The database must also contain seed data - for this a provided script can be used.

2. An external chrome must be running - either script or docker-compose can be used to start it. Another possibility is to use `docker run -d -p 4444:4444 selenium/standalone-chrome` command

3. Environment variables must be set for the DATABASE\_URL, TOPIC\_ID, CONFIGURATION\_ID and ACCOUNT\_ID

After all of this is done, the created docker container can be run using `docker run -it --net=host [NAME]` which will open bash terminal in the container.
To run the bot in this terminal, simply run `main.py` file.


We also provided multiple scripts (contained in the root of the directory) that can be used to start chrome and multiple selenium bots.

### Running the headless mode

To run the bot in a headless mode, an environment variable `YAUDIT_RUN_HEADLESS` needs to be set to `true`.

### Running in normal mode

When running the bot in docker container, a browser is required to run normally. To achieve this a separate container must be running,
which can be started by running `docker run -d -p 4444:4444 selenium/standalone-chrome`
