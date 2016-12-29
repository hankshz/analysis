# Analysis Framework
## About
This is an attempt to create an analysis framework that is very flexible to across multiple servers.
- It uses **Mongodb** as the database.
- It uses **Spark** along with **Anaconda** as the analysis tool
- It uses **Celery** for background workers

## Prerequirement
It is only tested under Ubuntu 14.04 and probably only supports Ubuntu.

## Setup
run the following steps in the top directory and accept/yes for every thing
```bash
    make setup develop
```
You need to restart the terminal after that

## Start Celery
```bash
    celery -A poll.task.tasks worker --loglevel=info
```
Or you can setup it as part of the startup service

## Existing tools
Besides the fact that you can access Celery task or even the database directly.
Some tools are already created to simplify the life.
You can use -h to see the details.
### Accounts
```bash
    accounts.py add --username xyz --consumer_key 123 --consumer_secret 456 --access_token_key 789 --access_token_secret abc
```
### Tasks
```bash
    tasks.py pull tweet --keyword Trump
    tasks.py pull timeline --screen_name realDonaldTrump
```

## Use Spark with Anaconda
For interactive
```bash
    pyspark
```
To run script
```bash
    spark_submit xyz.py
```
