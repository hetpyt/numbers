#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
import mysql.connector as sql
from mysql.connector.errors import Error as SQLError
from statemachine import AbstractStateMachine
from soundspeaker import SoundSpeaker
import loggingwrapper as log

class State(Enum):
    IDLE = 0
    GREETING = 1
    ACC_SELECTION = 2
    WAIT_FOR_NUMBER = 10
    WAIT_FOR_DECISION = 11
    READY_FOR_HANGOFF = 20

# создается при получении входящего звонка, отвечает за логику приема данных от абонента
class Operator(AbstractStateMachine):
    def __init__(self, config, caller_number):
        super(Operator, self).__init__(State.IDLE)
        # флаг ошибки базы данных
        self._db_error = False
        # параметры объекта
        self._caller_number = caller_number
        self._accounts = {}
        self._current_acc = None
        self._current_meter = None
        self._personal_greeting_message = None
        # параметры подключения к бд
        self._db_host = config["db_server"]
        self._db_port = config["db_port"]
        self._db_database = config["db_name"]
        self._db_user = config["db_user"]
        self._db_password = config["db_pass"]
        # параметры спикера
        self._speaker = SoundSpeaker(config["sp_resource_path"])
        self._greeting_message = config["sp_greeting_message"]
        self._error_message = config["sp_error_message"]
    
    def _trim_acc_number(self, acc_num):
        n = 0
        while n < len(acc_num):
            if acc_num[n].isdigit() and acc_num[n] != '0':
                break
            n += 1
        return acc_num[n:]
        
    def _speak_error(self):
        # произносит стандратное сообщение об ошибке. блокирует основной цикл
        try:
            self._speaker.speakAndWait([self._error_message])
        except Exception as e:
            log.exception("can't speak error sound sequence")
        
    def _greeting(self):
        # приветствие. вызывается после приема входящего вызова
        if not self._db_error:
            # нет ошибок бд - можно продолжать обработку звонка
            if self._personal_greeting_message:
                # задано персональное приветствие для данного номер телефона - пытаемся воспроизвести его
                # если не получается то воспроизводим стандартное
                if not self._begin_speaking(self._personal_greeting_message, False):
                    self._begin_speaking(self._greeting_message)
            else:
                # персональное приветствие не задано - воспроизводим стандартное
                self._speaker.speak(self._greeting_message)
        else:
            # была ошибка бд - не можем дальше продолжать обработку звонка
            self._speak_error()
            self._set_state(State.READY_FOR_HANGOFF)
            
    def _begin_speaking(self, sound, critical = True):
        snd = sound
        if not isinstance(sound, list) and not isinstance(sound, tuple):
            snd = [sound]
        try:
            self._speaker.speak(snd)
        except Exception as e:
            log.exception("can't speak sound sequence '{}'.".format(snd))
            if critical:
                log.error("end the call due to an exception while speaking critical sound sequence")
                self._set_state(State.READY_FOR_HANGOFF)
            return False
        return True
        
    def _stop_speaking(self):
        self._speaker.stop()
    
    def _is_speaking(self):
        return self._speaker.is_playing()
        
    def isReadyForHangoff(self):
        return (self._get_state() == State.READY_FOR_HANGOFF)

    def tick(self):
        # вызывается диспетчером каждый цикл
        if not self._is_speaking():
            # ничего не говорим можно "делать вещи"
            if self._get_state() == State.GREETING:
                # с этапа приветствия переходим к этапу выбора лс - если их несколько
                
            
        

    def stopSpeaking(self):
        self._speaker.stopAll()
        
    def processSymbol(self, symbol):
        # вызывается диспетчером для передачи символа от абонента
        if self._get_state() == State.GREETING:
            # получен символ во время приветствия
            # прерываем приветствие и продолжаем
            self._stop_speaking()

    def beginCallProcessing(self):
        # заупск машины состояний оператора на обработку алгоритма приема показаний
        self._set_state(State.GREETING)
        self._greeting()

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
        
        log.debug("collectes accounts : {}".format(self._accounts.))
        return True
        
    