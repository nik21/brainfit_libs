from logging import getLogger

from django.conf import settings
import zmq
from zmq.eventloop.zmqstream import ZMQStream


class Pipe:
    socket = None  # Socket connection
    _socket_configuration = None  # Configuration, loaded from PIPES
    _pipe_name = None  # Channel name
    _side = None  # Pipe side (pub, sub, req, rep, push, pull)
    _prefix = None  # Prefix for message filtering. Use with "sub" direction
    _socket_mode = None  # Режим работы сокета

    def __init__(self, pipe_name, side, prefix=''):
        self._pipe_name = pipe_name
        self._side = side
        self._prefix = prefix

        logger.debug('Get pipe configuration %s for %s', pipe_name, side)
        for name, item in settings.PIPES.items():
            if name == pipe_name:
                self._socket_configuration = item
                address = self._get_mode()
                self._connect(address, prefix)
                return
        raise Exception('Requested pipe "%s" is not found. Check your settings file' % pipe_name)

    def _get_mode(self):
        bus_type = self._socket_configuration.get('type', None)
        bus_pattern = self._socket_configuration.get('pattern', None)
        bus_configuration = self._socket_configuration.get('configuration', ('', '',))

        if bus_type == 'forwarder' or bus_pattern == 'pub/sub':
            available_directions = ('pub', 'sub',)
            if self._side == 'pub':
                self._socket_mode = zmq.PUB
            elif self._side == 'sub':
                self._socket_mode = zmq.SUB
        elif bus_type == 'streamer' or bus_pattern == 'push/pull':
            available_directions = ('push', 'pull')
            if self._side == 'push':
                self._socket_mode = zmq.PUSH
            elif self._side == 'pull':
                self._socket_mode = zmq.PULL
        elif bus_type == 'queue' or bus_pattern == 'req/rep':
            available_directions = ('req', 'rep',)
            if self._side == 'req':
                self._socket_mode = zmq.REQ
            elif self._side == 'rep':
                self._socket_mode = zmq.REP
        else:
            raise Exception('Invalid configuration for %s. Unknown type/pattern', self._pipe_name)

        if not self._socket_mode:
            raise Exception('You\'re must use %s device only with correct direction: %s' %
                            (self._pipe_name, available_directions))

        if self._side == available_directions[0]:
            return bus_configuration[0]
        elif self._side == available_directions[1]:
            return bus_configuration[1]
        else:
            raise Exception('Invalid direction for %s. Available only %s' % (self._pipe_name, available_directions))

    def _connect(self, address, prefix):
        if not address:
            raise Exception('Invalid socket address')
        context = zmq.Context()
        self.socket = context.socket(self._socket_mode)
        if self._socket_mode == zmq.SUB:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, prefix)
        self.socket.connect(address)

    def subscribe(self, callback):
        if not self.socket:
            raise Exception('A socket is not opened')
        ew_subscribe = ZMQStream(self.socket)
        ew_subscribe.on_recv(callback)

    def send_json(self, obj, flags=0, **kwargs):
        return self.socket.send_json(obj, flags=0, **kwargs)

    def send_string(self, u, flags=0, copy=True, encoding='utf-8'):
        return self.socket.send_string(u, flags, copy, encoding)


logger = getLogger(__name__)
