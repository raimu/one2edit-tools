#!/usr/bin/env python
#coding:utf-8

import httplib
import urllib
from lxml import etree


class One2EditError(Exception):
    pass


class ServerError(One2EditError):
    pass


class CommandError(One2EditError):
    pass


class Connection(object):

    def __init__(self, connection, username, password, client):
        self._connection = connection
        self._username = username
        self._password = password
        self._client = client
        self.document = Document(self)

    def raw_command(self, command, **kwargs):
        kwargs['command'] = command
        kwargs['clientId'] = self._client
        kwargs['authUsername'] = self._username
        kwargs['authPassword'] = self._password
        param = urllib.urlencode(kwargs)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        self._connection.request("POST", "/Api.php", param, headers)
        response = self._connection.getresponse()
        data = response.read()
        self._connection.close()
        if response.status != 200:
            raise ServerError()
        return data

    def command(self, command, **kwargs):
        xml = self.raw_command(command, **kwargs)
        root = etree.fromstring(xml)
        if root.tag != 'success':
            raise CommandError(root.find('code').text,
                               root.find('message').text)
        return root


class Document(object):

    def __init__(self, connection):
        self.connection = connection

    def info(self, id_, preview=False, groups=True, jobs=True, workflow=True,
             metadata=True):
        return self.connection.command(command='document.info',
                                       id=id_,
                                       includePreview=preview,
                                       includeContentGroups=groups,
                                       includeJobs=jobs,
                                       includeWorkflow=workflow,
                                       includeMetadata=metadata)

    def pdf(self, id_, preset=None):
        if preset is None:
            return self.connection.raw_command('document.export.pdf', id=id_)
        else:
            return self.connection.raw_command('document.export.pdf', id=id_,
                                               preset_id=preset)

    def thumbnail(self, id_):
        return self.connection.raw_command(command='document.preview', id=id_)


def get_connection(url, user, password, client):
    return Connection(httplib.HTTPConnection(url), user, password, client)
