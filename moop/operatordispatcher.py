#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from globals import __MAIN_LOOP_DELAY__
from statemachine import AbstractStateMachine
import loggingwrapper as log
import atprotocol
import aoperator

class State(Enum):
    IDLE = 0
    TEST = 1
    INIT = 2
    RINGING = 3
    ANSWER = 4
    ANSWERED = 5
    ENDINGCALL = 6
    DEVICE_ERROR = 11

# задержка между тестами ствязи (AT)
TICKS_BETWEEN_TEST = int(60 / __MAIN_LOOP_DELAY__) # 60 сек. выполняется тольк в состоянии IDLE

# получает сообщения от устройства связи и обрабатывает их управляя экземляром класс Operator 
class OperatorDispatcher(AbstractStateMachine):
    
    def __init__(self, config):
        # инициализация машины состояний
        super(OperatorDispatcher, self).__init__(State.IDLE)
        
        self._config = config
        
        # self._prev_state = None
        # self._state = State.IDLE
        
        self._caller_number = None
        
        self._operator = None
        
        self._ticks_from_last_test = 0
     
    def _end_call(self):
        self._set_state(State.ENDINGCALL)
        self._protocol.cmdEndCall()
        
    def _test(self):
        self._ticks_from_last_test = 0
        self._set_state(State.TEST)
        self._protocol.cmdTest()
    
    def _err_operator_call(self):
        self._set_def_state()
        # сообщаем оператору что вызов завершен с ошибкой
        if self._operator:
            self._operator.onCallEnded(True)

    
    def initProtocol(self, protocol):
        # установка событий
        protocol.setAction(atprotocol.ON_TICK, self.on_tick)
        protocol.setAction(atprotocol.ON_CMD_SENT, self.on_cmd_sent)
        protocol.setAction(atprotocol.ON_CMD_RESULT, self.on_cmd_result)
        protocol.setAction(atprotocol.ON_INCOMING_CALL, self.on_incoming_call)
        protocol.setAction(atprotocol.ON_END_CALL, self.on_end_call)
        protocol.setAction(atprotocol.ON_CALLER_NUMBER_RECIEVED, self.on_caller_number_recieved)
        protocol.setAction(atprotocol.ON_DTMF_RECIEVED, self.on_DTMF_recieved)
        protocol.setAction(atprotocol.ON_PROTOCOL_ERROR, self.on_protocol_error)
        protocol.setAction(atprotocol.ON_CMD_TIMEOUT, self.on_cmd_timeout)
        protocol.setAction(atprotocol.ON_UNKNOWN_MSG, self.on_unknown_msg)
        
        self._protocol = protocol
        
    # вызывается из главного цикла каждую итерацию для мониторинга таймаутов
    def on_tick(self):
        st = self._get_state()
        if st in (State.IDLE, State.DEVICE_ERROR):
            # плюсуем счетчик тестов тольк ов IDLE
            self._ticks_from_last_test += 1
            if self._ticks_from_last_test >= TICKS_BETWEEN_TEST:
                self._test()
        
        if self._operator:
            # если есть оператор то дергаем его
            self._operator.tick()
            if self._operator.isReadyForHangoff() and not self._get_state() == State.ENDINGCALL:
                # оператор готов завершить звонок
                self._end_call()
    
    def on_cmd_sent(self, cmd):
        log.debug("command {} sent".format(cmd))
    
    def on_cmd_result(self, cmd, result, test_result):
        log.debug("recieved result of {} with {}".format(cmd, result))
        st = self._get_state()
        # если состояние тестирования
        if st == State.TEST:
            if result:
                # тест прошел успешно
                log.debug("TEST OK")
            else:
                # ошибка проверки связи
                # raise ATConnectionLostError("no connection")
                log.error("TEST command return not OK")
            # возврат в состояние ожидания
            self._set_def_state()

        # если состояние ответа на входящий вызов        
        elif st == State.ANSWER:
            if result:
                # вызов успешно принят
                self._set_state(State.ANSWERED)
                # начало обработки звонка оператором
                self._operator.beginCallProcessing()
                # проверяем готовность в on_tick
            else:
                # ждем нового гудка для повтора ответа
                self._operator = None
                self._set_def_state()
                
        # если состояние завершение вызова
        elif st == State.ENDINGCALL:
            if result:
                # завершили вызов
                self._set_def_state()
                self._operator = None
                
            else:
                # ошибка команды завершения вызова - повтор команды
                self._end_call()
                
    # вызывается протоколом при превышении времени ожидания ответа команды
    def on_cmd_timeout(self, cmd):
        # вероятно потеряна связь с устройством либо устройство зависло
        log.error("command '{}' timed out. drop to def state".format(cmd))
        # сбрасываем состояние в ошибку
        self._err_operator_call()

    # вызывается при ошибке протокола
    def on_protocol_error(self):
        # вероятно потеряна связь с устройством либо устройство зависло
        log.error("protocol has some error. drop to def state")
        # сбрасываем состояние в ошибку
        self._err_operator_call()
        
    def on_incoming_call(self):
        log.debug("incoming call")
        if self._get_state() == State.IDLE:
            self._set_state(State.RINGING)
    
    # событие при окончании вызова с той стороны
    def on_end_call(self):
        if self._get_state() in (State.ANSWERED, State.ANSWER, State.RINGING):
            log.debug("call is ended on the other side")
        else:
            log.error("unexpected event on state '{}'! Dropped to IDLE.".format(self._get_state()._name_))
            self._set_def_state()
        # нужно известить оператора о том что вызов завершен
        if self._operator:
            self._operator.onCallEnded()
        
    def on_caller_number_recieved(self, number):
        log.debug("caller number recieved {}".format(number))
        # тут уже отвечаем на вызов
        if self._get_state() == State.RINGING:
            self._caller_number = number
            # создаем оператора
            self._operator = aoperator.Operator(self._config, number)
            # получем информацию о звонящем из бд
            self._operator.prepareForAnswer()
            # переходим на этам ответа на звонок
            self._set_state(State.ANSWER)
            self._protocol.cmdAnswerCall()
            
        else:
            log.error("unexpected event on state '{}'! Dropped to IDLE.".format(self._get_state()._name_))
            self._set_def_state()
            
    def on_DTMF_recieved(self, symbol):
        log.debug("DTMF sybol recieved {}".format(symbol))
        # получен символ - пересылаем текущему оператору
        if self._operator:
            self._operator.processSymbol(symbol)
        
    def on_unknown_msg(self, message):
        log.error("unknown message recieved {}".format(message))
    
    
    