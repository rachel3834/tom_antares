# import os
# os.environ['DJANGO_SETTINGS_MODULE'] = 'tom_antares.tests.test_settings'
from django.tests import TestCase
from unittest import mock

from antares_client._api.models import Alert, Locus

from tom_antares.antares import get_available_streams, get_stream_choices, AntaresBrokerForm, AntaresBroker
from tom_antares.tests.factories import AlertFactory, LocusFactory
from tom_alerts.alerts import get_service_class, get_service_classes
from tom_targets.models import Target
from tom_dataproducts.models import ReducedDatum




locus = Locus(locus_id='ANT2020aeczfyy', ra=159.6231717, dec=59.839694,
              properties={'ztf_object_id': 'ZTF20achooum',
                          'ztf_ssnamenr': 'null',
                          'num_alerts': 3,
                          'num_mag_values': 1,
                          'oldest_alert_id': 'ztf_candidate:1375506740015015002',
                          'oldest_alert_magnitude': 18.615400314331055,
                          'oldest_alert_observation_time': 59129.50674769981,
                          'newest_alert_id': 'ztf_candidate:1375506740015015002',
                          'newest_alert_magnitude': 18.615400314331055,
                          'newest_alert_observation_time': 59129.50674769981,
                          'brightest_alert_id': 'ztf_candidate:1375506740015015002',
                          'brightest_alert_magnitude': 18.615400314331055,
                          'brightest_alert_observation_time': 59129.50674769981},
              tags=['in_m31'],
              alerts=[
                  Alert(alert_id='ztf_upper_limit:ZTF20achooum-1372493490015', mjd=59126.493495400064)
              ]
            )


class TestAntaresBrokerClass(TestCase):
    def setUp(self):
        self.test_target = Target.objects.create(name='ZTF20achooum')
        self.Locus = LocusFactory.create()
        print(self.Locus)
        print(self.Locus.alerts)

# if __name__ == '__main__':
#     unittest.main()
