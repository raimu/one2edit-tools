#!/usr/bin/env python
#coding:utf-8

import unittest
import httplib
import xml.etree.ElementTree as etree
from mock import Mock
from one2edit.api import Connection
from one2edit.api import ServerError
from one2edit.api import CommandError


class ConnectionTestCase(unittest.TestCase):

    def test_inti(self):
        Connection(httplib.HTTPConnection('example.com'), 'username',
                   'password', 'client')


class ConnectionRawCommand(unittest.TestCase):

    know_commands = (
        ('document.info', {'id': 1}),
        ('document.export.pdf', {'id': 1}),
        ('client.info', {'id': 1}),
    )

    def setUp(self):
        self.mock = Mock()
        self.one = Connection(self.mock, 'username@example.com', 'password',
                              'client')

    def check_reqest(self, reqest, **kwargs):
        method, url, body, headers = reqest[0]
        body = body.split('&')
        self.assertEqual(method, 'POST')
        self.assertEqual(url, '/Api.php')
        self.assertEqual(headers['Content-type'],
                         'application/x-www-form-urlencoded')
        self.assertEqual(headers['Accept'], 'text/plain')
        self.assertIn('authUsername=username%40example.com', body)
        self.assertIn('authPassword=password', body)
        self.assertIn('clientId=client', body)
        for key in kwargs:
            self.assertIn('%s=%s' % (key, kwargs[key]), body)

    def check_response(self, return_data):
        self.assertTrue(self.mock.getresponse.called)
        self.assertTrue(self.mock.getresponse.return_value.read.called)
        self.assertTrue(self.mock.close.called)
        self.assertEqual(
            self.mock.getresponse.return_value.read.return_value, return_data
        )

    def test_raw_command(self):
        for command, kwargs in self.know_commands:
            self.mock.getresponse.return_value.status = 200
            self.one.raw_command(command)
            return_data = self.one.raw_command(command, **kwargs)
            kwargs['command'] = command
            self.check_reqest(self.mock.request.call_args, **kwargs)
            self.check_response(return_data)
            self.mock.reset_mock()

    def test_http_error(self):
        self.mock.getresponse.return_value.status = 500
        self.assertRaises(ServerError, self.one.raw_command, 'command')
        self.assertRaises(ServerError, self.one.command, 'command')


class HttpSuccess(unittest.TestCase):

    def setUp(self):
        self.mock = Mock()
        self.one = Connection(self.mock, 'username@example.com', 'password',
                              'client')
        self.mock.getresponse.return_value.status = 200
        self.mock.getresponse.return_value.read.return_value = '<success />'

    def test_command(self):
        data = self.one.command('document.info', id=1)
        self.assertEqual(etree.tostring(data), '<success />')

    def test_command_error(self):
        self.mock.getresponse.return_value.status = 200
        self.mock.getresponse.return_value.read.return_value = '<error />'
        self.assertRaises(CommandError, self.one.command, 'command', id=1)


if __name__ == '__main__':
    unittest.main()
