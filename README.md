Gather Specimens
================

This project gathers records from the Wayback Machine and stores them in a database
for extra processing.

# Configuration

## config.json

The database configuration is expected as a JSON mapping:

```json
{
    "user": "user",
    "pass": "password",
    "host": "postgres.database.url",
    "port": 5432,
    "database": "database"
}
```

## input.json

URLs for scanning are expected as a JSON list:

```json
[
    "magic.wizards.com/en/events",
    "magic.wizards.com/en/MTGO",
    "www.wizards.com/Magic/Magazine",
    "www.wizards.com/default.asp",
    "magic.wizards.com/en/news",
    "wizards.com/Magic/Magazine",
    "wizards.com/default.asp",
    "magic.wizards.com/en/articles"
]
```

# Process

## cdxrecords

With configuration set up, run `cdxrecords`. This:

- scans over each URL in the JSON file
- stores each gathered CDX record reported by Wayback in the database.

CDX records are tuples of information that can be used to get 'mementos' from Wayback's Memento API.
Storing these in the database means that the CDX API doesn't need to be queried after the initial gathering.

## celeryworker, celerygatherer

Assuming you have a lot of CDX records, the next steps require some setup.

### RabbitMQ server

Follow the instructions at https://www.rabbitmq.com/docs/download to install RabbitMQ on a server of your choice.

### Configure celery

Copy `celeryconfig.py.example` to `celeryconfig.py` and fill in the `broker_url` with the values used when installing RabbitMQ.

### Setting up a worker machine

Copy this source code (including `celeryconfig.py`) onto a worker machine and install it with Poetry in the normal way.
Also, ensure that the worker machine has connectivity to the RabbitMQ server.

Once installed, run

```bash
$ celery -A celeryworker worker --loglevel INFO --pool=gevent --concurrency=4
```

This runs the `celeryworker.py` script and registers with the RabbitMQ server as a worker.

Repeat for as many workers as desired (tested up to 12 workers with no issues).

### Setting up a driver machine

Copy this source code (including `celeryconfig.py`) onto a driver machine and install it with Poetry in the normal way.
Also, ensure that the driver machine has connectivity to the RabbitMQ server.

Once installed, run

```bash
$ python celerygatherer.py  [--start <position>] [--chunk-size <chunk-size>]
```

This script:
- pulls CDX records out of the database in chunks of `chunk-size` (default: 1000), starting at position `position` (default: 0).
- creates processing jobs for all CDX records that:
  - have not already been gathered
  - have not already failed gathering
  - have a 2xx or a 3xx status code
- gathers the results of the worker processing

A processing job (run on a worker) pulls the Memento data from the Wayback Memento API and stores it in the database.