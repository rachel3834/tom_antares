# Antares TOM Broker Module

This module adds [Antares](https://antares.noao.edu/) support to the TOM
Toolkit. Using this module TOMs can query and listen to Antares streams.

## Installation:

Install the module into your TOM environment:

    pip install tom-antares

Add `tom_antares.antares.AntaresBroker` to the `TOM_ALERT_CLASSES` in your TOM's
`settings.py`:

    TOM_ALERT_CLASSES = [
        'tom_alerts.brokers.mars.MARSBroker',
        ...
        'tom_antares.antares.ANTARESBroker'
    ]

## Running the tests

In order to run the tests, run the following in your virtualenv:

`python tom_antares/tests/run_tests.py`
