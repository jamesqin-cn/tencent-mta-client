# -*- coding:utf-8 -*-
__author__ = 'james'

import hashlib
import hmac
import logging
from datetime import date, datetime, timedelta

import requests
from tinyretry import RetryUntilForJson

import sys
if sys.version_info.major == 2:
    # Python2
    from urllib import quote
else:
    # Python3
    from urllib.parse import quote


MTA_RET_CODE_SUCCESS = 60000


def GetEveryDay(begin_date, end_date):
    step = 1 if begin_date <= end_date else -1
    date_list = []
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    while True:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        if begin_date == end_date:
            break
        begin_date += timedelta(days=step)
    return date_list


class MtaClient():
    def __init__(self, app_id, app_key):
        self._mta_http_client = HttpClient(app_id, app_key)

    def GetUserActiveData(self, start_date, end_date):
        idx = "10201,10202,10203"
        data = self._mta_http_client.GetDataFromMtaServer(
            "/ctr_active_anal/get_offline_data", start_date, end_date, idx)
        date_list = GetEveryDay(start_date, end_date)
        new_data = []
        for date in date_list:
            new_row = {'stat_date': date}
            if date in data["ret_data"]:
                new_row.update(data["ret_data"][date])
            new_data.append(new_row)
        return new_data

    def GetUserBasicData(self, start_date, end_date):
        # 优先获取准确度更高的离线统计数据
        data = self._GetUserBasicDataOffline(start_date, end_date)
        if int(data["ret_code"]) != MTA_RET_CODE_SUCCESS:
            return None
        # 如果是24小时内的数据可能还没转入离线计算，则需要从实时接口拉取数据填补缺失的部分
        if end_date not in data["ret_data"]:
            rt_data = self._GetUserBasicDataRealTime(end_date, end_date)
            if "Date" in rt_data["ret_data"] and rt_data["ret_data"]["Date"] == end_date:
                data["ret_data"][end_date] = rt_data["ret_data"]
        date_list = GetEveryDay(start_date, end_date)
        new_data = []
        for date in date_list:
            if date in data["ret_data"]:
                new_row = {
                    'stat_date': date,
                    "NewUser": data["ret_data"][date]["NewUser"],
                    "NewUser_repeat": data["ret_data"][date]["NewUser"],
                    "ActiveUser": data["ret_data"][date]["ActiveUser"],
                    "TotalUser": data["ret_data"][date]["TotalUser"],
                    "SessionCount": data["ret_data"][date]["SessionCount"]
                }
                # 如果MTA服务器提供了 NoRepeatUser，则用不重复用户修正 NewUser
                if 'NoRepeatUser' in data["ret_data"][date]:
                    new_row["NewUser"] = data["ret_data"][date]["NoRepeatUser"]
            else:
                new_row = {
                    "stat_date": date,
                    "NewUser": 0,
                    "NewUser_repeat": 0,
                    "ActiveUser": 0,
                    "TotalUser": 0,
                    "SessionCount": 0
                }
            new_data.append(new_row)
        return new_data

    # 1天内的数据应从实时数据接口获取, 实时数据不支持10106指标 NoRepeatUser
    def _GetUserBasicDataRealTime(self, start_date, end_date):
        idx = "10101,10102,10103,10104,10105"
        return self._mta_http_client.GetDataFromMtaServer("/ctr_user_basic/get_realtime_data", start_date, end_date, idx)

    # 1天前的数据应从离线数据接口获取, 离线数据支持10106指标NoRepeatUser
    def _GetUserBasicDataOffline(self, start_date, end_date):
        idx = "10101,10102,10103,10104,10105,10106"
        return self._mta_http_client.GetDataFromMtaServer("/ctr_user_basic/get_offline_data", start_date, end_date, idx)


class HttpClient():
    def __init__(self, app_id=None, app_key=None, entry_point='https://openapi.mta.qq.com'):
        self._app_id = app_id
        self._app_key = app_key
        self._entry_point = entry_point

    def SetAppKey(self, app_id, app_key):
        self._app_id = app_id
        self._app_key = app_key
        return self

    def Sign(self, token, data):
        data = data.replace('~', '%7E')
        token = token.replace('-', '+').replace('_', '/')
        m = hmac.new(bytes(token.encode('utf-8')), data.encode('utf-8'), hashlib.sha1)
        data = hashlib.md5(m.hexdigest().encode('utf-8'))
        return data.hexdigest()

    def BuildRequestUrl(self, path, start_date, end_date, idx):
        params = {
            "app_id": self._app_id,
            "start_date": start_date,
            "end_date": end_date,
            "idx": idx
        }
        params = [(k, params[k]) for k in sorted(params.keys())]
        arr_query_string = []
        for row in params:
            arr_query_string.append("{}={}".format(row[0], row[1]))
        query_str = "&".join(arr_query_string)
        base_url = "{}{}?{}".format(self._entry_point, path, query_str)
        source_str = "GET&{}&{}".format(
            path.replace("/", "%2F"), quote(query_str))
        url = "{}&sign={}".format(
            base_url, self.Sign(self._app_key+'&', source_str))
        return url

    @RetryUntilForJson("ret_code", MTA_RET_CODE_SUCCESS, 3, 2)
    def DoGet(self, url, timeout=10):
        try:
            logging.info(u"Start get %s" % (url))
            resp = requests.get(url, timeout=timeout)
        except requests.RequestException as e:
            logging.info(u'catch request exception, errmsg is: ' + e.message)
            return None
        finally:
            logging.info(u"Finish get %s" % (url))

        return resp.json()

    def GetDataFromMtaServer(self, path, start_date, end_date, idx):
        url = self.BuildRequestUrl(path, start_date, end_date, idx)
        return self.DoGet(url)
