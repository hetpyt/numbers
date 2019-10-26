#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import mysql.connector as sql
from mysql.connector.errors import Error as SQLError
import loggingwrapper as log

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
    
    def _db_connect(self):
        conn = None
        
        if not sql.paramstyle == 'pyformat':
            log.error('sql paramstyle = "{}" not supported.'.format(sql.paramstyle))
            return conn
            
        tryes = 3
        while tryes > 0:
            try:
                conn = sql.connect(
                    host = self._db_host,
                    port = self._db_port, 
                    database = self._db_database,
                    user = self._db_user,
                    password = self._db_password)
                    
                tryes = 0
                
            except SQLError as e:
                tryes -= 1
                log.exception("can't connect to database server")
                
        return conn

    def isError(self):
        return self._db_error
        
    def fetchCallerInfo(self):
        
        conn = self._db_connect()
        
        if not conn:
            self._db_error = True
            return
        
        cursor = conn.cursor(dictionary = True)
        request_text = """SELECT 
            `clients`.`id` AS `client_id`,
            `clients`.`account`,
            `clients`.`phone_number`,
            `clients`.`registration_date`,
            `meters`.`id` AS `meter_id`,
            `meters`.`index_num`,
            `meters`.`updated`,
            `meters`.`count`,
            `pers_set`.`greeting_f`
            FROM `clients` 
            INNER JOIN `meters` ON `meters`.`owner_id` = `clients`.`id` AND `clients`.`phone_number`=%(phone)s
            LEFT JOIN `pers_set` ON `pers_set`.`phone_number`=%(phone)s"""
            
        try:
            cursor.execute(request_text, {'phone' : self._caller_number})
            
            for item in cursor.fetchall():
                acc = item["account"]
                
                if not acc in self._accounts:
                    self._accounts[acc] = []
                    
                mtr = item.copy()
                # поле для новых показаний
                mtr[DB_MTR_NEWCOUNT] = mtr[DB_MTR_COUNT]
                self._accounts[acc].append(mtr)
                self._personal_greeting_f = item[DB_PERSONAL_GREATING]
                
        except SQLError as e:
            self._db_error = True
            log.exception("can't fetch data from database")
            
        finally:
            cursor.close()
            conn.close()
            
        # определение функции для извлечения ключа сортировки
        def sf(item):
            return item[DB_MTR_INDEX]
            
        # сортировка по номеру в УС
        for acc in self._accounts:
            self._accounts[acc].sort(key = sf)
            
        # инициализация итератора для обхода лицевых счетов
        self._accounts_iter = iter(self._accounts)
        
        log.debug("collected accounts : {}".format(list(self._accounts.keys())))
    
    def storeData(self):
        conn = self._db_connect()
        need_commit = False
        
        if not conn:
            self._db_error = True
            return
        
        cursor = conn.cursor(dictionary = True)
        
        # request_text = """UPDATE `meters` 
            # SET `updated` = %(date)s, 
            # `count` = %(count)s 
            # WHERE `meters`.`id` = %(meter_id)s"""

        request_text = """INSERT INTO `meters_readings` 
        (`id`, `meter_id`, `count`, `updated`)
        VALUES (NULL, '%(meter_id)s', '%(count)s', %(date)s)"""
        
        try:
            now_d = datetime.now()
            for acc in self._accounts:
                # цикл по ЛС
                for meter in self._accounts[acc]:
                    # цикл по счетчикам
                    #if meter["__data_confirmed__"]:
                    cursor.execute(request_text, {'meter_id' : meter["meter_id"], 'count' : meter["count"], 'date' : now_d})
                    log.debug("update row in 'meters' with id '{}'".format(meter["meter_id"]))
                    need_commit = True
                        
            if need_commit:
                conn.commit()
                
        except SQLError as e:
            self._db_error = True
            log.exception("can't update data into database")
            
        finally:
            cursor.close()
            conn.close()
        
            
