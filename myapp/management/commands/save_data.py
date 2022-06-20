from django.core.management.base import BaseCommand
from tom_targets.models import Target
from tom_alerts.brokers.mars import MARSBroker
from tom_antares.antares import ANTARESBroker

class Command(BaseCommand):

    help = 'Downloads data for all completed observations'

    def add_arguments(self, parser):
        parser.add_argument('--ztf', help='Download data for a single target')

    def handle(self, *args, **options):
        print('options -> ', options)
        # targets = Target.objects.filter(name=options['ztf'])
        # print('targets -> ', targets)
        targets = Target.objects.all()
        print(targets)
        targets.filter(name = 'ZTF17aadevsj').delete()
        print(targets)

        # mars_broker = MARSBroker()
        # mars_alerts = mars_broker.fetch_alerts({'objectId': options['ztf']})
        # mars_alert_list = list(mars_alerts)

        # mars_broker.to_target(mars_alert_list[0])
        
        antares_broker = ANTARESBroker()
        alerts = antares_broker.fetch_alerts({'ztfid': 'ZTF17aadevsj'})
        antares_alert_list = list(alerts)
        print(len(antares_alert_list))
        alert0 = antares_alert_list[0]

        key_list = alert0['properties'].keys()
        for k in key_list:
            print(k, '--', alert0['properties'][k])
            # print(k)
        # print(antares_broker.alert_to_dict(antares_alert_list[0]))

        # targets = Target.objects.all()
        # print(targets)

        return 'Success!'