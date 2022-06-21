from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker

class Command(BaseCommand):

    help = 'Downloads data for all completed observations'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        # WATCH OUT!!! this line deletes all tagets at the beginning of the script
        # are you sure this is what you want to do?
        Target.objects.all().delete()
        
        #start a MARSBroker and get the alerts
        mars_broker = MARSBroker()
        mars_alerts = mars_broker.fetch_alerts({'objectId': options['ztf']})
        mars_alert_list = list(mars_alerts)
        alert = mars_alert_list[0]

        mars_properties = {}
        for k in alert['candidate'].keys():
            mars_properties['mars_' + k] = alert['candidate'][k]

        #create target
        try:
            target = Target.objects.get(name = options['ztf'])
        except:
            target = mars_broker.to_target(alert)

        target.save(extras = mars_properties)
        print('done with mars')
        
        #start an antares broker and geth the alerts
        antares_broker = ANTARESBroker()
        antares_alerts = antares_broker.fetch_alerts({'ztfid': options['ztf']})
        antares_alert_list = list(antares_alerts)
        #if we are filtering for an obj_id there should only be one but it returns an iterator so it must be indexed
        alert = antares_alert_list[0]
        
        #redefines the keys of the alet to be preceded by "antares_"
        antares_properties = {}
        for k in alert['properties'].keys():
            antares_properties['antares_{}'.format(k)] = alert['properties'][k]

        target.save(extras = antares_properties)
        return 'Success!'