#!/usr/bin/env python
#coding:utf-8

import unittest
import mock
from one2edit.api import Document


class TestCase(unittest.TestCase):

    def setUp(self):
        self.mock = mock.Mock()
        self.document = Document(self.mock)

    def test_info(self):
        return_value = self.document.info(1, metadata=False)
        self.mock.command.assert_called_once_with(command='document.info',
                                                  id=1,
                                                  includePreview=False,
                                                  includeContentGroups=True,
                                                  includeJobs=True,
                                                  includeWorkflow=True,
                                                  includeMetadata=False)
        self.assertEqual(return_value, self.mock.command.return_value)

    def test_preview(self):
        return_value = self.document.thumbnail(1)
        self.mock.raw_command.assert_called_once_with(
            command='document.preview', id=1)
        self.assertEqual(return_value, self.mock.raw_command.return_value)
        

if __name__ == '__main__':
    unittest.main()
