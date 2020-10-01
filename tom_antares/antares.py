from datetime import datetime, timezone
import logging
import requests

from antares_client import StreamingClient
from antares_client.exceptions import AntaresException
from antares_client.search import get_by_ztf_object_id
from django import forms
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import marshmallow

from tom_alerts.alerts import GenericBroker, GenericQueryForm, GenericAlert
from tom_targets.models import Target, TargetName

logger = logging.getLogger(__name__)

ANTARES_BASE_URL = 'https://antares.noirlab.edu'
ANTARES_API_URL = 'https://api.antares.noirlab.edu'
ANTARES_TAG_URL = ANTARES_API_URL + '/v1/tags'


def get_available_streams(url=ANTARES_TAG_URL):
    response = requests.get(url).json()
    streams = response.get('data', {})
    if response.get('links', {}).get('next'):
        return streams + get_available_streams(response['links']['next'])
    return streams


def get_stream_choices():
    streams = get_available_streams()
    return [(s['id'], s['id']) for s in streams]


class AntaresBrokerForm(GenericQueryForm):
    stream = forms.ChoiceField(choices=get_stream_choices)


class AntaresBroker(GenericBroker):
    name = 'Antares'
    form = AntaresBrokerForm

    def __init__(self, *args, **kwargs):
        try:
            antares_creds = settings.BROKER_CREDENTIALS['antares']
            self.config = {
                'api_key': antares_creds['api_key'],
                'api_secret': antares_creds['api_secret']
            }
            if antares_creds.get('group'):
                self.config['group'] = antares_creds['group']

        except KeyError:
            raise ImproperlyConfigured('Missing ANTARES API credentials')

    def fetch_alerts(self, parameters):
        print(parameters)
        stream = parameters['stream']
        client = StreamingClient([stream], **self.config)
        alert_stream = client.iter()
        alerts = []
        while len(alerts) < 20:
            try:
                alert = next(alert_stream)
            except (AntaresException, marshmallow.exceptions.ValidationError):
                break
            alerts.append(alert)
        return iter(alerts)

    def fetch_alert(self, id):
        # Antares doesn't have programmatic access to alerts, so we use MARS here
        # url = 'https://mars.lco.global/?format=json&candid={}'.format(id)
        # response = requests.get(url)
        # response.raise_for_status()
        # return response.json()['results'][0]
        alert = get_by_ztf_object_id(id)
        return alert

    def process_reduced_data(self, target, alert=None):
        pass

    def to_target(self, alert):
        _, alert = alert
        print(alert)
        target = Target.objects.create(
            identifier=alert.locus_id,
            name=alert.properties['ztf_object_id'],
            type='SIDEREAL',
            ra=alert.ra,
            dec=alert.dec,
        )
        if alert.properties.get('horizons_targetname'):
            TargetName.objects.create(target=target, name=alert.properties.get('horizons_targetname'))
        return target

    def to_generic_alert(self, alert):
        # print(alert)
        # _, alert = alert
        # print(alert)
        # url = 'https://antares.noao.edu/loci/{}'.format(alert['new_alert']['alert_id'])
        # timestamp = datetime.utcfromtimestamp(alert['timestamp_unix']).replace(tzinfo=timezone.utc)
        # return GenericAlert(
        #     timestamp=timestamp,
        #     url=url,
        #     id=alert['new_alert']['properties']['ztf_candid'],
        #     name=alert['new_alert']['properties']['ztf_object_id'],
        #     ra=alert['new_alert']['ra'],
        #     dec=alert['new_alert']['dec'],
        #     mag=alert['new_alert']['properties']['ztf_magpsf'],
        #     score=alert['new_alert']['properties']['ztf_rb']
        # )
        _, alert = alert
        url = f'{ANTARES_BASE_URL}/loci/{alert.locus_id}'
        timestamp = datetime.utcfromtimestamp(alert.newest_alert_observation_time).replace(tzinfo=timezone.utc)
        return GenericAlert(
            timestamp=timestamp,
            url=url,
            id=alert.locus_id,
            name=alert.properties['ztf_object_id'],
            ra=alert.ra,
            dec=alert.dec,
            mag=alert.properties.get('newest_alert_magnitude', ''),
            score=alert.alerts[-1].properties.get('ztf_rb', '')
        )
