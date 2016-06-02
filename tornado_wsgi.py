# coding: utf-8

from __future__ import unicode_literals

import datetime
import tornado.web
import tornado.wsgi

from middleware import TestMiddle
from server import WSGIServer


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("this is a tornado wsgi application")


if __name__ == "__main__":
    application = tornado.web.Application([
        (r"/", MainHandler),
    ])
    wsgi_app = tornado.wsgi.WSGIAdapter(application)
    server = WSGIServer(('', 9090))
    server.set_application(TestMiddle(wsgi_app))
    print 'RAPOWSGI Server Serving HTTP service on port {0}'.format(9090)
    print '{0}'.format(datetime.datetime.now().
                       strftime('%a, %d %b %Y %H:%M:%S GMT'))
    server.serve_forever()
