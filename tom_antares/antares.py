import logging
import requests

from antares_client import StreamingClient
from antares_client.exceptions import AntaresException
from antares_client.search import get_by_ztf_object_id
from astropy.time import Time, TimezoneInfo
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
    return [(s['id'] + '_staging', s['id']) for s in streams]


class AntaresBrokerForm(GenericQueryForm):
    # TODO: allow multiple selection of streams
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
            if antares_creds.get('group'):  # Group should only be set if it exists, otherwise Antares manages it
                self.config['group'] = antares_creds['group']

        except KeyError:
            raise ImproperlyConfigured('Missing ANTARES API credentials')

    def fetch_alerts(self, parameters):
        print(f'parameters: {parameters}')
        stream = parameters['stream']
        client = StreamingClient([stream], **self.config)
        alert_stream = client.iter(20)
        alerts = []
        # TODO: Add timeout in case there aren't alerts
        while len(alerts) < 5:  # TODO: change this back to 20
            try:
                alert = next(alert_stream)
            except (AntaresException, marshmallow.exceptions.ValidationError):
                break
            serialized_alert = {
                'locus_id': alert[1].locus_id,
                'ra': alert[1].ra,
                'dec': alert[1].dec,
                'properties': alert[1].properties,
                'tags': alert[1].tags,
                'lightcurve': alert[1].lightcurve.to_json(),
                'catalogs': alert[1].catalogs,
                'alerts': [{
                    'alert_id': alert.alert_id,
                    'mjd': alert.mjd,
                    'properties': alert.properties} for alert in alert[1].alerts]
            }
            alert = (alert[0], serialized_alert)
            alerts.append(alert)
        return iter(alerts)

    def fetch_alert(self, id):
        alert = get_by_ztf_object_id(id)
        return alert

    def process_reduced_data(self, target, alert=None):
        pass

    def to_target(self, alert):
        _, alert = alert
        target = Target.objects.create(
            identifier=alert['locus_id'],
            name=alert['properties']['ztf_object_id'],
            type='SIDEREAL',
            ra=alert['ra'],
            dec=alert['dec'],
        )
        if alert['properties'].get('horizons_targetname'):
            TargetName.objects.create(target=target, name=alert['properties'].get('horizons_targetname'))
        return target

    def to_generic_alert(self, alert):
        _, alert = alert
        url = f"{ANTARES_BASE_URL}/loci/{alert['locus_id']}"
        timestamp = Time(
            alert['properties'].get('newest_alert_observation_time'), format='mjd', scale='utc'
        ).to_datetime(timezone=TimezoneInfo())
        return GenericAlert(
            timestamp=timestamp,
            url=url,
            id=alert['locus_id'],
            name=alert['properties']['ztf_object_id'],
            ra=alert['ra'],
            dec=alert['dec'],
            mag=alert['properties'].get('newest_alert_magnitude', ''),
            score=alert['alerts'][-1]['properties'].get('ztf_rb', '')
        )
