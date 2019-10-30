#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#TODO после ввода новых показаний и отказа от подтверждения диктует вы ввели.  

from enum import Enum
#import mysql.connector as sql
#from mysql.connector.errors import Error as SQLError
from globals import __MAIN_LOOP_DELAY__, __NO_SOUND__, __NO_SQL__
from statemachine import AbstractStateMachine
if __NO_SQL__:
    import dbwrapperstub as db
else:
    import mysqlwrapper as db
import loggingwrapper as log

if __NO_SOUND__:
    from soundspeakerstub import SoundSpeaker
    log.debug("NO SOUND. used stub.")
else:
    from soundspeaker import SoundSpeaker

SYM_CONFIRM = '*'
SYM_CANCEL = '#'

TICKS_INPUT_TIMEOUT = int(30 / __MAIN_LOOP_DELAY__) # 60 сек. выполняется тольк в состоянии IDLE


class State(Enum):
    IDLE = 0
    GREETING = 1
    ACC_SELECTION = 2
    METER_SELECTION = 4
    NUMBER_INPUT = 10
    ACC_CONFIRMATION = 11
    DATA_CONFIRMED = 18
    DATA_STORED = 19
    READY_FOR_HANGOFF = 20

# создается при получении входящего звонка, отвечает за логику приема данных от абонента
class Operator(AbstractStateMachine):
    def __init__(self, config, caller_number):
        super(Operator, self).__init__(State.IDLE)
        
        self._number_input = ''
        
        self._speaking = False
        
        self._input_timeout = None
        
        # параметры объекта
        self._caller_number = caller_number
        
        self._accounts = {}
        self._accounts_iter = None
        self._accounts_alldone = False
        self._current_acc = None
        
        self._meter_iter = None
        self._meter_alldone = False
        self._current_meter = None
        
        self._personal_greeting_message = None

        # параметры спикера
        self._speaker = SoundSpeaker(config["sp_resource_path"])
        self._greeting_message = config["sp_greeting_message"]
        self._error_message = config["sp_error_message"]
        self._noacc_message = config["sp_noacc_message"]
        self._acc_selection1 = config["sp_acc_selection1"]
        self._acc_selection2 = config["sp_acc_selection2"]
        self._mtr_question1 = config["sp_mtr_question1"]
        self._mtr_question2 = config["sp_mtr_question2"]
        self._mtr_question3 = config["sp_mtr_question3"]
        self._mtr_newvalue = config["sp_mtr_newvalue"]
        self._mtr_confirmation1 = config["sp_mtr_confirmation1"]
        self._mtr_confirmation2 = config["sp_mtr_confirmation2"]
        self._mtr_confirmation3 = config["sp_mtr_confirmation3"]
        self._mtr_stored = config["sp_mtr_stored"]
        self._farewell_message = config["sp_farewell_message"]
        
        self._db = db.DBConnector(config)
        
    def _trim_acc_number(self, acc_num):
        n = 0
        while n < len(acc_num):
            if acc_num[n].isdigit() and acc_num[n] != '0':
                break
            n += 1
        return acc_num[n:]
    
    def _convert_number(self, num, mode = 0):
        if mode:
            return self._speaker.convert_by_groups(self._trim_acc_number(num), 3)
        else:
            return self._speaker.convert(num)
    
    def _number_input_add(self, symbol):
        if symbol.isdecimal():
            self._number_input += symbol
    
    def _number_input_reset(self):
        self._number_input = ''
    
    def _number_input_exists(self):
        return bool(self._number_input)
    
    # вызывается после подтверждения ввода числа абонентом и сохраняет введенное значение
    # в качестве новых показаний. 
    def _number_input_confirm(self):
        if self._number_input:
            self._current_meter[db.DB_MTR_COUNT_NEW] = int(self._number_input)
        # сброс ввода
        self._number_input_reset()
    
    def _set_input_timeout(self):
        self._input_timeout = TICKS_INPUT_TIMEOUT
    
    def _reset_input_timeout(self):
        self._input_timeout = None
    
    def _reset_meter_iter(self):
        self._meter_iter = iter(self._accounts[self._current_acc])
    
    def _next_account(self):
        try:
            # получаем следующий лс из итератора
            self._current_acc = next(self._accounts_iter)
            # инициализируем итератор счетчиков
            self._reset_meter_iter()
            
        except StopIteration as e:
            self._current_acc = None
            self._accounts_alldone = True
        
        return  not self._accounts_alldone
    
    def _next_meter(self):
        try:
            self._current_meter = next(self._meter_iter)
            
        except StopIteration as e:
            self._current_meter = None
            self._meter_alldone = True
        
        return  not self._meter_alldone
    
    def _speak_error(self):
        # произносит стандратное сообщение об ошибке.
        self._set_state(State.READY_FOR_HANGOFF)
        try:
            #self._speaker.speakAndWait([self._error_message])
            self._begin_speaking([self._error_message])
        except Exception as e:
            log.exception("can't speak error sound sequence")
            
    # приветствие. вызывается после приема входящего вызова
    def _greeting(self):
        self._set_state(State.GREETING)
        if not self._db.isError():
            # нет ошибок бд - можно продолжать обработку звонка
            if self._personal_greeting_message:
                # задано персональное приветствие для данного номер телефона - пытаемся воспроизвести его
                # если не получается то воспроизводим стандартное
                if not self._begin_speaking(self._personal_greeting_message, False):
                    self._begin_speaking(self._greeting_message)
            else:
                # персональное приветствие не задано - воспроизводим стандартное
                self._begin_speaking(self._greeting_message)
        else:
            # была ошибка бд - не можем дальше продолжать обработку звонка
            self._speak_error()
            
    # прощание - вызывается в конце вызова
    def _farewell(self):
        self._set_state(State.READY_FOR_HANGOFF)
        self._begin_speaking([self._farewell_message])
        
    # инициализирует начало ввода последовательности цифр абонентом
    def _begin_number_input(self):
        self._number_input_reset()
        self._set_state(State.NUMBER_INPUT)
        self._begin_speaking([self._mtr_newvalue,
                            self._convert_number(self._current_meter[db.DB_MTR_INDEX])])

    
    def _meter_selection(self, goto_next = True):
        self._set_state(State.METER_SELECTION)
        # если нужно переходить к следующему счетчику
        if goto_next:
            self._next_meter()
        
        if self._current_meter:
            # есть текущий счетчик - воспроизводим сообщение 
            self._begin_speaking([self._mtr_question1,
                                        self._convert_number(self._current_meter[db.DB_MTR_INDEX]),
                                        self._mtr_question2,
                                        self._convert_number(self._current_meter[db.DB_MTR_COUNT]),
                                        self._mtr_question3])
        else:
            # счетчики кончились
            # диктуем что навводил абонент и спрашиваем подтверждение
            self._set_state(State.ACC_CONFIRMATION)
            # сформируем последовательность для воспроизведения
            ps = []
            for mtr in self._accounts[self._current_acc]:
                ps.append(self._mtr_confirmation1)
                ps += self._convert_number(mtr[db.DB_MTR_INDEX])
                ps.append(self._mtr_confirmation2)
                ps += self._convert_number(mtr[db.DB_MTR_COUNT_NEW])
            ps.append(self._mtr_confirmation3)
            self._begin_speaking(ps)

    
    def _acc_selection(self, goto_next = True):
        acc_cnt = len(self._accounts)
        if acc_cnt == 0:
            # нет ни одного лс
            self._set_state(State.READY_FOR_HANGOFF)
            self._begin_speaking([self._noacc_message, self._farewell_message])
            
        # elif acc_cnt == 1:
            # # только один лс - пропускаем выбор лс
            # if goto_next:
                # self._next_account()
            # else:
                # self._reset_meter_iter()
            # self._meter_selection()
            
        else:
            # более нуля лс
            self._set_state(State.ACC_SELECTION)
            if goto_next:
                self._next_account()
            else:
                self._reset_meter_iter()
                
            if self._current_acc:    
                # есть еще лс
                if acc_cnt == 1:
                    # сразу переходим к счетчикам
                    self._meter_selection()
                else:
                    # читаем только если более одного лс
                    self._begin_speaking([self._acc_selection1, 
                                            self._convert_number(self._current_acc, 1), 
                                            self._acc_selection2])
            else:
                # лс больше нету - прощаемся
                self._farewell()
            
    def _begin_speaking(self, sound, critical = True):
        if not isinstance(sound, list) and not isinstance(sound, tuple):
            snd = [sound]
        else:
            snd = []
            for item in sound:
                if item:
                    if isinstance(item, list) or isinstance(item, tuple):
                        snd += list(item)
                    else:
                        snd.append(item)
            
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
        return self._speaker.isSpeaking()
        
    # вызывается диспетчером для проверки готовности оператора завершить вызов   
    def isReadyForHangoff(self):
        # возвращает истину если состояние READY_FOR_HANGOFF и не соспроизводится сообщение
        return (self._get_state() == State.READY_FOR_HANGOFF and not self._speaking)

    # вызывается диспетчером когда вызов завершается с той строны
    def onCallEnded(self, error_state = False):
        if error_state:
            self._speak_error()
        self._set_state(State.READY_FOR_HANGOFF)
        
    # вызывается диспетчером каждый цикл
    def tick(self):
        # проверяем закончили ли мы говорить
        old_speaking = self._speaking
        self._speaking = self._is_speaking()
        # если старые статус был Да а новый Нет то мы закончили говорить
        ended_speaking = (old_speaking == True and self._speaking == False)
        if ended_speaking:
            # закончили говорить можно "делать вещи"
            st = self._get_state()
            if st == State.GREETING:
                # с этапа приветствия переходим к этапу выбора лс - если их несколько
                self._acc_selection()
                
            elif st = State.DATA_CONFIRMED:
                # проговорили абоненту о том что показания приняты - переходим к следующему лс
                self._acc_selection()
                
            # установка таймаута    
            if st in (State.ACC_SELECTION, State.METER_SELECTION, State.NUMBER_INPUT, State.ACC_CONFIRMATION):
                # если закончили говорить и состояния требующие реакции абонента то запускаем таймаут
                self._set_input_timeout()
                
        if not self._input_timeout == None:
            # если есть таймаут то уменьшаем его
            self._input_timeout -= 1
            if self._input_timeout <= 0:
                # время вышло. пользователь не отреагировал - прощаемся и завершаем вызов
                self._set_state(State.READY_FOR_HANGOFF)
                self._begin_speaking([self._farewell_message])
            
    def stopSpeaking(self):
        self._speaker.stopAll()
        
    # вызывается диспетчером для передачи символа от абонента
    def processSymbol(self, symbol):
        # ввод символа абонентом всегда прерывает воспроизведение звука
        self._stop_speaking()
        # сброс таймаута
        self._reset_input_timeout()
        st = self._get_state()
        if st == State.ACC_SELECTION:
            # выбор аккаунта
            if symbol == SYM_CONFIRM:
                # выбор лс подтвержден - переходим к выбору счетчика
                self._meter_selection()
                
            elif symbol == SYM_CANCEL:
                # выбор лс не подтвержден - переходим к следующему лс, если есть
                self._acc_selection()
                
            else:
                # введен левый символ - игнорим
                pass
        
        elif st == State.METER_SELECTION:
            # выбор счетчика
            if symbol == SYM_CONFIRM:
                # выбор счетчика подтвержден - переходим к вводу числа
                self._begin_number_input()
                
            elif symbol == SYM_CANCEL:
                # выбор счетчика не подтвержден - переходим к следующему счетчику
                self._meter_selection()
                
            else:
                # введен левый символ - игнорим
                pass
                
        elif st == State.NUMBER_INPUT:
            # ввод числа - показаний
            if symbol == SYM_CONFIRM:
                # ввод числа окончен и подтвержден
                # сохраняем введенное значение в качестве новых показаний по текущему счетчику
                self._number_input_confirm()
                # возвращаемся к выбору счетчика
                self._meter_selection()
                
            elif symbol == SYM_CANCEL:
                # ввод числа окончен и подтвержден
                if self._number_input_exists():
                    # если были введены символы, то считаем что абонент желает ввести поновой (например в случае ошибки)
                    self._begin_number_input()
                    
                else:
                    # не было ввода символов - переходим к следующему счетчику
                    self._number_input_confirm()
                    self._meter_selection()
                
            else:
                # введен символ числа - проверим
                self._number_input_add(symbol)
        
        elif st == State.ACC_CONFIRMATION:
            # подтверждение ввода показаний
            if symbol == SYM_CONFIRM:
                # ввод подтвержден - сохраняем в бд
                self._db.storeData(self._accounts)
                if self._db.isError():
                    # ошибка записи в бд
                    self._speak_error()
                else:
                    # данные записаны успешно - сообщаем пользователю
                    self._set_state(State.DATA_CONFIRMED)
                    self._begin_speaking([self._mtr_stored])
                    #self._acc_selection()
                    
            elif symbol == SYM_CANCEL:
                # ввод отклонен - возвращаеся к вводу показаний по текущему лс поновой
                self._acc_selection(False)
                
            else:
                # введен левый символ - игнорим
                pass

    def prepareForAnswer(self):
        self._accounts, self._personal_greeting_f = self._db.fetchCallerInfo(self._caller_number)
        self._accounts_iter = iter(self._accounts)

    def beginCallProcessing(self):
        # заупск машины состояний оператора на обработку алгоритма приема показаний
        self._greeting()
            
