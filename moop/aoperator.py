#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector as sql
from mysql.connector.errors import Error as SQLError
from soundspeaker import SoundSpeaker
import loggingwrapper as log

# создается при получении входящего звонка, отвечает за логику приема данных от абонента
class Operator:
    def __init__(self, config, caller_number):
        # флаг готовности к завершению вызова
        self._ready_for_hangoff = False
        # флаг ошибки базы данных
        self._db_error = False
        # параметры объекта
        self._caller_number = caller_number
        self._accounts = {}
        self._personal_greeting_f = None
        # параметры подключения к бд
        self._db_host = config["db_server"]
        self._db_port = config["db_port"]
        self._db_database = config["db_name"]
        self._db_user = config["db_user"]
        self._db_password = config["db_pass"]
        # параметры спикера
        self._speaker = SoundSpeaker(config["sp_resource_path"])
        self._greeting = config["sp_greeting_filename"]
        self._error_message = config["sp_error_message"]

    def isReadyForHangoff(self):
        return self._ready_for_hangoff

    def speakGreeting(self):
        if not self._db_error:
            if self._personal_greeting_f:
                if not self._speaker.speak([self._personal_greeting_f]):
                    self._speaker.speak([self._greeting])
            else:
                self._speaker.speak([self._greeting])
        else:
            self.speakError()
            self._ready_for_hangoff = True
            
    def speakError(self):
        self._speaker.speakAndWait([self._error_message])
        
    def getCallerAccounts(self):
        pass
    
    def fetchCallerInfo(self):
        conn = None
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
        
        if not conn:
            self._db_error = True
            return False
        
        cursor = conn.cursor(dictionary = True)
        request_text = "SELECT `clients`.`id` AS `client_id`,\
            `clients`.`account`,\
            `clients`.`phone_number`,\
            `clients`.`registration_date`,\
            `meters`.`id` AS `meter_id`,\
            `meters`.`updated`,\
            `meters`.`updated_from_db`,\
            `meters`.`count`,\
            `meters`.`count_from_db`,\
            `pers_set`.`greeting_f`\
            FROM `clients` \
            INNER JOIN `meters` ON `meters`.`owner_id` = `clients`.`id` AND `clients`.`phone_number`='{}'\
            LEFT JOIN `pers_set` ON `pers_set`.`phone_number`='{}'".format(self._caller_number, self._caller_number)
            
        try:
            cursor.execute(request_text)
        except SQLError as e:
            self._db_error = True
            log.exception("can't fetch dsta from database")
            return False

        for item in cursor.fetchall():
            acc = item["account"]
            if not acc in self._accounts:
                self._accounts[acc] = []
            self._accounts[acc].append(item.copy())
            self._personal_greeting_f = item["greeting_f"]
            log.debug('data:{}'.format(item))
        
        return True
        
    