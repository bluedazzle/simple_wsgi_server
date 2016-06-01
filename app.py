# coding: utf-8
from __future__ import unicode_literals
from wsgiref import simple_server


def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world from a RAPOWSGI application!\n']
