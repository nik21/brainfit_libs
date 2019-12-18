from django.core.management.base import BaseCommand
from brainfit_libs.applications.bus.application import start_zmq_forwarders


class Command(BaseCommand):
    help = 'Starts the 0MQ Forwarder application'
    server = None

    def shutdown(self):
        """Stop server and add callback to stop i/o loop"""
        self.server.stop()

    def handle(self, *args, **options):
        start_zmq_forwarders()

