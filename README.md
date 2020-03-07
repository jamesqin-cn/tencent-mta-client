# Tencent MTA Client

## What is Tencent MTA Client?
腾讯移动数据分析平台（[MTA](https://mta.qq.com/mta/ctr_index/opd)）的python SDK

## Programming Language
- python 2.7
- python 3.7

## Installation
```
pip install tencent-mta-client 
```

## Quick Start
```
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
```


## Functions List
- 应用基本指标
- 应用基本指标
- Other（按需封装，欢迎pull request or mail to me）