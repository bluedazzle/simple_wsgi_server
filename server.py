# coding: utf-8
from __future__ import unicode_literals

import socket
import StringIO
import sys
import datetime

from middleware import TestMiddle
from wsgiref import simple_server


class WSGIServer(object):
    socket_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 10

    def __init__(self, address):
        self.socket = socket.socket(self.socket_family, self.socket_type)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(address)
        self.socket.listen(self.request_queue_size)
        host, port = self.socket.getsockname()[:2]
        self.host = host
        self.port = port

    def set_application(self, application):
        self.application = application

    def serve_forever(self):
        while 1:
            self.connection, client_address = self.socket.accept()
            self.handle_request()

    def handle_request(self):
        self.request_data = self.connection.recv(1024)
        self.request_lines = self.request_data.splitlines()
        try:
            self.get_url_parameter()
            env = self.get_environ()
            app_data = self.application(env, self.start_response)
            self.finish_response(app_data)
            print '[{0}] "{1}" {2}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                           self.request_lines[0], self.status)
        except Exception, e:
            pass

    def get_url_parameter(self):
        self.request_dict = {'Path': self.request_lines[0]}
        for itm in self.request_lines[1:]:
            if ':' in itm:
                self.request_dict[itm.split(':')[0]] = itm.split(':')[1]
        self.request_method, self.path, self.request_version = self.request_dict.get('Path').split()

    def get_environ(self):
        env = {
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': StringIO.StringIO(self.request_data),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'REQUEST_METHOD': self.request_method,
            'PATH_INFO': self.path,
            'SERVER_NAME': self.host,
            'SERVER_PORT': self.port,
            'USER_AGENT': self.request_dict.get('User-Agent')
        }
        return env

    def start_response(self, status, response_headers):
        headers = [
            ('Date', datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')),
            ('Server', 'RAPOWSGI0.1'),
        ]
        self.headers = response_headers + headers
        self.status = status

    def finish_response(self, app_data):
        try:
            response = 'HTTP/1.1 {status}\r\n'.format(status=self.status)
            for header in self.headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in app_data:
                response += data
            self.connection.sendall(response)
        finally:
            self.connection.close()


if __name__ == '__main__':
    port = 8888
    if len(sys.argv) < 2:
        sys.exit('请提供可用的wsgi应用程序, 格式为: 模块名.应用名')
    elif len(sys.argv) > 2:
        port = sys.argv[2]


    def generate_server(address, application):
        server = WSGIServer(address)
        server.set_application(TestMiddle(application))
        return server


    app_path = sys.argv[1]
    module, application = app_path.split('.')
    module = __import__(module)
    application = getattr(module, application)
    httpd = generate_server(('', int(port)), application)
    print 'RAPOWSGI Server Serving HTTP service on port {0}'.format(port)
    print '{0}'.format(datetime.datetime.now().
                       strftime('%a, %d %b %Y %H:%M:%S GMT'))
    httpd.serve_forever()
