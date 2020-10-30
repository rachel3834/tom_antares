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
        'tom_antares.antares.AntaresBroker'
    ]

You'll need Antares credentials to use this plugin. You can register for an account [here](https://antares.noao.edu/accounts/register/). Add your Antares credentials to your project
's `settings.py`:

    BROKERS = {
        'anatares': {
            'api_key': 'YOUR ANTARES API KEY',
            'api_secret': 'YOUR ANTARES API SECRET'
        }
    }

## Running the tests

In order to run the tests, run the following in your virtualenv:

`python tom_antares/tests/run_tests.py`
