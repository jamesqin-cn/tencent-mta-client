# -*- coding: utf-8 -*-
__author__ = 'james'

import logging
import time
import unittest

from tencent.mta.client import MtaClient


class Test_MtaClient(unittest.TestCase):
    def setUp(self):
        self._mta = MtaClient("<your_api_id>", "<your_app_key>")

    def test_GetUserActiveData(self):
        data = self._mta.GetUserActiveData('2020-03-01', '2020-03-07')
        print(data)

    def test_GetUserBasicData(self):
        data = self._mta.GetUserBasicData('2020-03-01', '2020-03-07')
        print(data)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    unittest.main()
