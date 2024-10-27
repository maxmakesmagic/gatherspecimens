Gather Specimens
================

This project gathers records from the Wayback Machine and stores them in a database
for extra processing.

For Wizards-specific information, check out [WIZARDS.md](WIZARDS.md).

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

## (TODO) Parsing data and converting to Markdown

As per the information in [WIZARDS.md](WIZARDS.md), there are four distinct periods of Magic content-management-system:

- [The "Torment" era](WIZARDS.md#wwwwizardscomdefaultasp---january-1-2002)
- [The "Alara" era](WIZARDS.md#wwwwizardscommagicmagazine---august-26-2008)
- [The "Khans" era](WIZARDS.md#magicwizardscom---june-17-2014)
- [The "Bro" era](WIZARDS.md#magicwizardscom-2-electric-boogaloo---november-8-2022)

Each of these eras has an extractor which tries to extracts metadata from the document:

- Article title
- Author
- Column name (if a column article)
- Publishing date

as well as extracting the important content of the article itself, without any of the surrounding website navigation.

From this metadata a "path" is generated. This path fully describes the article in question and allows for deduplication of articles.

## (TODO) Deduplication

Content is compared based on similarity metrics (TODO: e.g. Levenshtein distance, fuzzy matching) to handle different revisions.

## Canonical URL generation

In order to make sure that every article is under a well-known path, we use the following canonical URL format:

  ```
  /type/year-month-day/author-or-column/identifier
  ```

- type: Whether the content is an article, news, or event.
- year-month-day: The publication date.
- author-or-column: A slugified version of the author’s name or the column title.
- identifier: The unique identifier for the article

### Examples of Enhanced Canonical URLs

http://www.wizards.com/Magic/Magazine/Article.aspx?x=mtg/daily/twtw/1 becomes
```
/article/2008-08-29/the-week-that-was/back-to-school
```

http://magic.wizards.com/en/articles/archive/welcome-new-magic-site-2014-06-17 becomes
```
/article/2014-06-17/feature/welcome-to-the-new-magic-site
```

## (TODO) Image Handling

A script is used to scrape images and/or ensure URLs point to still-hosted versions of images.

## (TODO) Dumping articles to folders

A script is used to dump articles to disk based on the canonical URL.
