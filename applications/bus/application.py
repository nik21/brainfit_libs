from logging import getLogger
from django.conf import settings
import zmq
import threading


class TForwarderDevice(threading.Thread):
    frontend_address = ''
    backend_address = ''
    name = ''

    def __init__(self, name, frontend_address, backend_address):
        self.frontend_address = frontend_address
        self.backend_address = backend_address
        self.name = name
        super().__init__()

    def run(self):
        try:
            context = zmq.Context()

            # Socket facing clients
            frontend = context.socket(zmq.SUB)
            frontend.bind(self.frontend_address)

            frontend.setsockopt_string(zmq.SUBSCRIBE, "")  # Python 3

            # Socket facing services
            backend = context.socket(zmq.PUB)
            backend.bind(self.backend_address)

            logger.debug('Cluster bus forwarder device (%s) %s->%s start success' % (
                self.name, self.frontend_address, self.backend_address,))
            zmq.device(zmq.FORWARDER, frontend, backend)
        except Exception as e:
            logger.debug('Cluster bus handle exception :(', e)
        finally:
            frontend.close()
            backend.close()
            context.term()


class TQueueDevice(threading.Thread):
    frontend_address = ''
    backend_address = ''
    name = ''

    def __init__(self, name, frontend_address, backend_address):
        self.frontend_address = frontend_address
        self.backend_address = backend_address
        self.name = name
        super().__init__()

    def run(self):
        try:
            context = zmq.Context()

            # Socket facing clients
            frontend = context.socket(zmq.XREP)
            frontend.bind(self.frontend_address)

            # Socket facing services
            backend = context.socket(zmq.XREQ)
            backend.bind(self.backend_address)

            logger.debug('Cluster bus queue device (%s) %s->%s start success' % (self.name, self.frontend_address,
                                                                                 self.backend_address,))
            zmq.device(zmq.QUEUE, frontend, backend)
        except Exception as e:
            logger.debug('Cluster bus handle :(', e)
        finally:
            frontend.close()
            backend.close()
            context.term()


class TStreamerDevice(threading.Thread):
    frontend_address = ''
    backend_address = ''
    name = ''

    def __init__(self, name, frontend_address, backend_address):
        self.frontend_address = frontend_address
        self.backend_address = backend_address
        self.name = name
        super().__init__()

    def run(self):
        try:
            context = zmq.Context()

            # Socket facing clients
            frontend = context.socket(zmq.PULL)
            frontend.bind(self.frontend_address)

            # Socket facing services
            backend = context.socket(zmq.PUSH)
            backend.bind(self.backend_address)

            logger.debug(
                'Cluster bus streamer device (%s) %s->%s start success' % (
                    self.name, self.frontend_address, self.backend_address,))
            zmq.device(zmq.STREAMER, frontend, backend)
        except Exception as e:
            logger.debug('Cluster bus handle :(', e)
        finally:
            frontend.close()
            backend.close()
            context.term()


def start_zmq_forwarders():
    for bus_name, item in settings.PIPES.items():
        bus_type = item.get('type', None)
        bus_pattern = item.get('pattern', None)
        bus_configuration = item.get('configuration', ('', '',))

        if bus_pattern == 'pub/sub':
            bus_type = 'forwarder'
        elif bus_pattern == 'push/pull':
            bus_type = 'streamer'
        elif bus_pattern == 'req/rep':
            bus_type = 'queue'

        if bus_type == 'forwarder':
            process = TForwarderDevice(bus_name, bus_configuration[0], bus_configuration[1])
            process.start()
        elif bus_type == 'streamer':
            process = TStreamerDevice(bus_name, bus_configuration[0], bus_configuration[1])
            process.start()
        elif bus_type == 'queue':
            process = TQueueDevice(bus_name, bus_configuration[0], bus_configuration[1])
            process.start()
        else:
            raise Exception('Invalid configuration for %s. Use "type" or "pattern" for configure PIPE' % bus_name)


logger = getLogger(__name__)

# http://www.slideshare.net/profyclub_ru/0-mq-low-latency
if __name__ == '__main__':
    start_zmq_forwarders()
