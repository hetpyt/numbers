#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from enum import Enum
import loggingwrapper as log
import atprotocol
import operator

class Stage(Enum):
    IDLE = 0
    TEST = 1
    INIT = 2
    RINGING = 3
    ANSWER = 4
    ANSWERED = 5

TICKS_BETWEEN_TEST = 100 # при 0.1 секунде задержки получаем ~ 30 сек

# получает сообщения от устройства связи и обрабатывает их управляя экземляром класс Operator 
class OperatorDispatcher:
    
    def __init__(self, config):
        self._config = config
        
        self._stage = Stage.IDLE
        
        self._caller_number = None
        
        self._operator = None
        # устанавливается на некое значение и уменьшается с каждым вызовом tick
        # если доходит до нуля, то команда считается не выполненной по таймауту
        self._cmd_result_timeout = None
        
        self._ticks_from_last_test = 0
        
    def _set_stage(self, stage):
        self._stage = stage
        # сброс таймаута
        self._cmd_result_timeout = None
        
    def _get_stage(self):
        return self._stage
        
    def _init_operator(self):
        pass
        
    def initProtocol(self, protocol):
        # установка событий
        protocol.setAction(atprotocol.ON_TICK, self.on_tick)
        protocol.setAction(atprotocol.ON_CMD_SENT, self.on_cmd_sent)
        protocol.setAction(atprotocol.ON_CMD_RESULT, self.on_cmd_result)
        protocol.setAction(atprotocol.ON_INCOMING_CALL, self.on_incoming_call)
        protocol.setAction(atprotocol.ON_END_CALL, self.on_end_call)
        protocol.setAction(atprotocol.ON_CALLER_NUMBER_RECIEVED, self.on_caller_number_recieved)
        protocol.setAction(atprotocol.ON_DTMF_RECIEVED, self.on_DTMF_recieved)
        protocol.setAction(atprotocol.ON_UNKNOWN_MSG, self.on_unknown_msg)
        
        self._protocol = protocol
    
    def on_tick(self):
        #print(self._ticks_from_last_test)
        self._ticks_from_last_test += 1
        
        if not self._cmd_result_timeout == None:
            self._cmd_result_timeout -= 1

        # вызывается из главного цикла каждую итерацию для мониторинга таймаутов
        if self._stage == Stage.IDLE:
            if self._ticks_from_last_test >= TICKS_BETWEEN_TEST:
                self._ticks_from_last_test = 0
                self._set_stage(Stage.TEST)
                self._cmd_result_timeout = 200
                self._protocol.cmdTest()
            return
            
        elif self._stage == Stage.TEST:
            # идет тестирование связи
            if self._cmd_result_timeout <= 0:
                pass
        
    # def processMessage(self, msg):
        # log.debug("process message {}".format(msg))
        # self._protocol.processMessage(msg)
    
    def on_cmd_sent(self, cmd):
        log.debug("command {} sent".format(cmd))
    
    def on_cmd_result(self, cmd, result, test_result):
        log.debug("recieved result of {} with {}".format(cmd, result))

        if self._stage == Stage.TEST:
            if result:
                # тест прошел успешно
                #self._ticks_from_last_test = 0
                self._set_stage(Stage.IDLE)
            else:
                # ошибка проверки связи
                # raise ATConnectionLostError("no connection")
                pass
                
        if self._stage == Stage.ANSWER:
            if result:
                # вызов успешно принят
                self._set_stage(Stage.ANSWERED)
                self._operator = operator.Operator(self._config, self._caller_number)
            else:
                # ждем ногово гудка для повтора ответа
                self._set_stage(Stage.IDLE)
        
    def on_incoming_call(self):
        log.debug("incoming call")
        if self._stage == State.IDLE:
            self._set_stage(Stage.RINGING)
        
    def on_end_call(self):
        log.debug("call ended")
        
    def on_caller_number_recieved(self, number):
        log.debug("caller number recieved {}".format(number))
        # тут уже отвечаем на вызов
        if self._stage == Stage.RINGING:
            self._set_stage(Stage.ANSWER)
            self._caller_number = number
            self._protocol.cmdAnswerCall()
        
    def on_DTMF_recieved(self, symbol):
        log.debug("DTMF sybol recieved {}".format(symbol))
        
    def on_unknown_msg(self, message):
        log.debug("unknown message recieved {}".format(message))
    
    
    