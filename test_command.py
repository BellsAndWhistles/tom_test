from django.test import TestCase
from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker

from tom_targets.models import Target, TargetName

mars_alert = {
    'candid': 617122521615015023,
    'candidate': {
       'b': 0.70548695469711,
       'dec': -10.5296018,
       'jd': 2458371.6225231,
       'l': 20.7124513780029,
       'magpsf': 16.321626663208,
       'ra': 276.5843017,
       'rb': 0.990000009536743,
       'wall_time': 'Mon, 10 Sep 2018 02:56:25 GMT',
    },
    'lco_id': 11296149,
    'objectId': 'ZTF18abbkloa',
}

antares_alert = {
    'locus_id' : 1,
    'ra' : 2,
    'dec' : 3,
    'properties' : {
        'ztf_object_id' : 'ZTF18abbkloa',
        'num_alerts' : 4
    },
    'tags' : ['lc_feature_extractor'],
    'catalogs' : [],
    'alerts' : []
    }
mars_alert_stream = []
antares_alert_stream = []

class AlertComboTestCase(TestCase):
    def setUp(self):
        #antares setup
        self.test_target = Target.objects.create(name='ZTF18abbkloa')
        # self.loci = [LocusFactory.create() for i in range(0, 5)]
        # self.locus = self.loci[0]  # Get an individual locus for testing
        # self.tag = 'in_m31'
        #mars setup
        alert_temp = mars_alert.copy()
        alert_temp['lco_id'] = 11053318
        alert_temp['objectId'] = 'ZTF18aberpsh'
        self.mars_alert_stream = iter([mars_alert, alert_temp])
        alert_temp = antares_alert.copy()
        alert_temp['properties']['ztf_object_id'] = 'ZTF18aberpsh'
        self.antares_alert_stream = iter([antares_alert, alert_temp])


    def test_alertcombo(self):
        #this code was just copied from the save_data.py file
        mars_broker = MARSBroker()
        mars_alerts = self.mars_alert_stream
        mars_alert_list = list(mars_alerts)
        for alert in mars_alert_list:
            try: #create target
                target = Target.objects.get(name = alert['objectId'])
            except:
                target = mars_broker.to_target(alert)
            #rename the dictionaty
            mars_properties = {}
            for k in alert['candidate'].keys():
                mars_properties['mars_' + k] = alert['candidate'][k]
            target.save(extras = mars_properties)
        
        #start an antares broker and geth the alerts
        antares_broker = ANTARESBroker()
        antares_alerts = self.antares_alert_stream
        antares_alert_list = list(antares_alerts)
        
        #if we are filtering for an obj id there should only be one but it returns an iterator so it must be indexed still
        for alert in antares_alert_list:
            try: #create target
                target = Target.objects.get(name = alert['properties']['ztf_object_id'])
            except:
                target = antares_broker.to_target(alert)
            #redefines the keys of the alert to be preceded by "antares_"
            antares_properties = {}
            for k in alert['properties'].keys():
                antares_properties['antares_{}'.format(k)] = alert['properties'][k]
            target.save(extras = antares_properties)

        targets = list(Target.objects.all())

        self.assertEqual(targets[0].name, self.test_target.name)
