#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loggingwrapper as log
from time import clock
from datetime import datetime
# имена ключевых полей бд
DB_MTR_INDEX = "index_num"
DB_MTR_COUNT = "count"
DB_MTR_UPDATED = "updated"
DB_PERSONAL_GREATING = "greeting_f"
# поля отсутсвующие в субд (служебные
DB_MTR_COUNT_NEW = "new_count"
DB_MTR_DATA_CHANGED = ""
DB_MTR_DATA_CONFIRMED = ""

class DBConnector:
    
    def __init__(self, config):
        
        # флаг ошибки базы данных
        self._db_error = False
        
        # параметры подключения к бд
        self._db_host = config["db_server"]
        self._db_port = config["db_port"]
        self._db_database = config["db_name"]
        self._db_user = config["db_user"]
        self._db_password = config["db_pass"]
    
        self._data = [
            {"client_id" : "1",
            "account" : "123456",
            "phone_number" : "+79115792506",
            "registration_date" : clock(),
            "meter_id" : 1,
            "index_num" : 1,
            "updated" : clock(),
            "count" : 100,
            "greeting_f" : ""},
            
            {"client_id" : "1",
            "account" : "123456",
            "phone_number" : "+79115651769",
            "registration_date" : clock(),
            "meter_id" : 2,
            "index_num" : 2,
            "updated" : clock(),
            "count" : 200,
            "greeting_f" : ""},
            
            {"client_id" : "2",
            "account" : "654321",
            "phone_number" : "+79115651769",
            "registration_date" : clock(),
            "meter_id" : 1,
            "index_num" : 1,
            "updated" : clock(),
            "count" : 303,
            "greeting_f" : ""}
        ]
    
    def _db_connect(self):
        pass
        
    def isError(self):
        return self._db_error
        
    def fetchCallerInfo(self, caller_number):
        start_time = clock()
        
        accounts = {}
        pers_gr = ""
        
        try:
            
            for item in self._data:
                if not item["phone_number"] == caller_number:
                    continue
                acc = item["account"]
                
                if not acc in accounts:
                    accounts[acc] = []
                    
                mtr = item.copy()
                # поле для новых показаний
                mtr[DB_MTR_COUNT_NEW] = mtr[DB_MTR_COUNT]
                accounts[acc].append(mtr)
                pers_gr = mtr[DB_PERSONAL_GREATING]
                
        except Exception as e:
            self._db_error = True
            log.exception("can't fetch data from database")
            
        finally:
            pass
            
        # определение функции для извлечения ключа сортировки
        def sf(item):
            return item[DB_MTR_INDEX]
            
        # сортировка по номеру в УС
        for acc in accounts:
            accounts[acc].sort(key = sf)
            
        log.debug("completed in {:g} sec.".format(clock() - start_time))
        log.debug("collected accounts : {}".format(list(accounts.keys())))
        
        return (accounts, pers_gr)
        
    def storeData(self, accounts):
        start_time = clock()
        
        try:
            now_d = datetime.now()
            for acc in accounts:
                # цикл по ЛС
                for meter in accounts[acc]:
                    # цикл по счетчикам
                    data_s = "stored data: meter_id={}, count={}, updated={}".format(meter["meter_id"], meter[DB_MTR_COUNT_NEW], now_d)
                    log.debug(data_s)
                    need_commit = True
                        
            if need_commit:
                pass
                
        except Exception as e:
            self._db_error = True
            log.exception("can't update data into database")
            
        finally:
            pass
        
        log.debug("completed in {:g} sec.".format(clock() - start_time))

