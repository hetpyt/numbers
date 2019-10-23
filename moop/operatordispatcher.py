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
        
    # def _set_state(self, state):
        # self._prev_state = self._state
        # self._state = state
        
    # def _get_state(self):
        # return self._state
        
    def initProtocol(self, protocol):
        # установка событий
        protocol.setAction(atprotocol.ON_TICK, self.on_tick)
        protocol.setAction(atprotocol.ON_CMD_SENT, self.on_cmd_sent)
        protocol.setAction(atprotocol.ON_CMD_RESULT, self.on_cmd_result)
        protocol.setAction(atprotocol.ON_INCOMING_CALL, self.on_incoming_call)
        protocol.setAction(atprotocol.ON_END_CALL, self.on_end_call)
        protocol.setAction(atprotocol.ON_CALLER_NUMBER_RECIEVED, self.on_caller_number_recieved)
        protocol.setAction(atprotocol.ON_DTMF_RECIEVED, self.on_DTMF_recieved)
        protocol.setAction(atprotocol.ON_CMD_TIMEOUT, self.on_cmd_timeout)
        protocol.setAction(atprotocol.ON_UNKNOWN_MSG, self.on_unknown_msg)
        
        self._protocol = protocol
    
    def on_tick(self):
        #print(self._ticks_from_last_test)
        self._ticks_from_last_test += 1
        
        # вызывается из главного цикла каждую итерацию для мониторинга таймаутов
        if self._state == State.IDLE:
            if self._ticks_from_last_test >= TICKS_BETWEEN_TEST:
                self._ticks_from_last_test = 0
                self._set_state(State.TEST)
                self._protocol.cmdTest()
                
        if self._operator:
            self._operator.tick()
    
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
            self._set_state(State.IDLE)

        # если состояние ответа на входящий вызов        
        elif st == State.ANSWER:
            if result:
                # вызов успешно принят
                self._set_state(State.ANSWERED)
                # начало обработки звонка оператором
                self._operator.beginCallProcessing()
                # проверяем готовность к завершению вызова
                if self._operator.isReadyForHangoff():
                    # завершаем вызов
                    self._set_state(State.ENDINGCALL)
                    self._protocol.cmdEndCall()
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
                self._protocol.cmdEndCall()
    
    def on_cmd_timeout(self, cmd):
        log.error("command '{}' timed out")
        
    def on_incoming_call(self):
        log.debug("incoming call")
        if self._get_state() == State.IDLE:
            self._set_state(State.RINGING)
        
    def on_end_call(self):
        log.debug("call ended")
        
    def on_caller_number_recieved(self, number):
        log.debug("caller number recieved {}".format(number))
        # тут уже отвечаем на вызов
        if self._get_state() == State.RINGING:
            self._caller_number = number
            # создаем оператора
            self._operator = aoperator.Operator(self._config, number)
            # получем информацию о звонящем из бд
            self._operator.fetchCallerInfo()
            # переходим на этам ответа на звонок
            self._set_state(State.ANSWER)
            self._protocol.cmdAnswerCall()
            
        else:
            log.error("unexpected event on state '{}'! Dropped to IDLE.".format(self._get_state()._name_))
            self._set_def_state()
            
    def on_DTMF_recieved(self, symbol):
        log.debug("DTMF sybol recieved {}".format(symbol))
        # получен символ - пересылаем текущему оператору
        self._operator.processSymbol(symbol)
        
    def on_unknown_msg(self, message):
        log.debug("unknown message recieved {}".format(message))
    
    
    