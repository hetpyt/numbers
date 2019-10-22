#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
from globals import __MAIN_LOOP_DELAY__
import loggingwrapper as log
import atprotocol
import aoperator

class Stage(Enum):
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
class OperatorDispatcher:
    
    def __init__(self, config):
        self._config = config
        
        self._prev_stage = None
        self._stage = Stage.IDLE
        
        self._caller_number = None
        
        self._operator = None
        
        self._ticks_from_last_test = 0
        
    def _set_stage(self, stage):
        self._prev_stage = self._stage
        self._stage = stage
        
    def _get_stage(self):
        return self._stage
        
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
        if self._stage == Stage.IDLE:
            if self._ticks_from_last_test >= TICKS_BETWEEN_TEST:
                self._ticks_from_last_test = 0
                self._set_stage(Stage.TEST)
                self._protocol.cmdTest()
    
    def on_cmd_sent(self, cmd):
        log.debug("command {} sent".format(cmd))
    
    def on_cmd_result(self, cmd, result, test_result):
        log.debug("recieved result of {} with {}".format(cmd, result))
        
        # если состояние тестирования
        if self._stage == Stage.TEST:
            if result:
                # тест прошел успешно
                log.debug("TEST OK")
            else:
                # ошибка проверки связи
                # raise ATConnectionLostError("no connection")
                log.error("TEST command return not OK")
            # возврат в состояние ожидания
            self._set_stage(Stage.IDLE)

        # если состояние ответа на входящий вызов        
        elif self._stage == Stage.ANSWER:
            if result:
                # вызов успешно принят
                self._set_stage(Stage.ANSWERED)
                # произносим приветствие
                self._operator.speakGreeting()
                # проверяем готовность к завершению вызова
                if self._operator.isReadyForHangoff():
                    # завершаем вызов
                    self._set_stage(Stage.ENDINGCALL)
                    self._protocol.cmdEndCall()
            else:
                # ждем нового гудка для повтора ответа
                self._operator = None
                self._set_stage(Stage.IDLE)
                
        # если состояние завершение вызова
        elif self._stage == Stage.ENDINGCALL:
            if result:
                # завершили вызов
                self._set_stage(Stage.IDLE)
                self._operator = None
                
            else:
                # ошибка команды завершения вызова - повтор команды
                self._protocol.cmdEndCall()
    
    def on_cmd_timeout(self, cmd):
        log.error("command '{}' timed out")
        
    def on_incoming_call(self):
        log.debug("incoming call")
        if self._stage == Stage.IDLE:
            self._set_stage(Stage.RINGING)
        
    def on_end_call(self):
        log.debug("call ended")
        
    def on_caller_number_recieved(self, number):
        log.debug("caller number recieved {}".format(number))
        # тут уже отвечаем на вызов
        if self._stage == Stage.RINGING:
            self._caller_number = number
            # создаем оператора
            self._operator = aoperator.Operator(self._config, number)
            # получем информацию о звонящем из бд
            self._operator.fetchCallerInfo()
            # переходим на этам ответа на звонок
            self._set_stage(Stage.ANSWER)
            self._protocol.cmdAnswerCall()
            
        else:
            log.error("unexpected event on stage '{}'! Dropped to IDLE.".format(self._stage._name_))
            self._set_stage(Stage.IDLE)
            
    def on_DTMF_recieved(self, symbol):
        log.debug("DTMF sybol recieved {}".format(symbol))
        
    def on_unknown_msg(self, message):
        log.debug("unknown message recieved {}".format(message))
    
    
    