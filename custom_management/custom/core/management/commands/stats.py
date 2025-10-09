from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Displays stats related to stuff'
    def handle(self, *args, **kwargs):
        try:
            name=kwargs['name']
            print(name)
        except:
            print("Hey")
    def add_arguments(self, parser):
        # return super().add_arguments(parser)
        parser.add_argument('-n','--name',help="Your custom name printing")