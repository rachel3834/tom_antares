from django.test import tag, TestCase

from tom_antares.antares import ANTARESBroker


@tag('canary')
class TestANTARESModuleCanary(TestCase):
    """NOTE: To run these tests in your venv: python ./tom_scimma/tests/run_tests.py"""

    def setUp(self):
        self.broker = ANTARESBroker()

    def test_boilerplate(self):
        self.assertTrue(True)

    def test_fetch_alerts(self):
        """Test fetch_alerts."""
        pass

    def test_fetch_alert(self):
        """Test fetch_alert."""
        pass

    def test_submit_upstream_alert(self):
        """Test submit_upstream_alert."""
        pass
