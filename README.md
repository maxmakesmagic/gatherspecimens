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