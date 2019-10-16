#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loggingwrapper as log
import atprotocol
import operator

# получает сообщения от устройства связи и обрабатывает их управляя экземляром класс Operator 
class OperatorDispatcher:
    
    def __init__(self):
        self._online = False
        self._caller_number = None
        
        
    def _init_operator(self):
        pass
        
    def initProtocol(self, serial_protocol):
        # инициирует протокол обмена с устройством связи
        protocol = atprotocol.ATProtocol(serial_protocol)
        # установка событий
        protocol.setAction(atprotocol.ON_CMD_SENT, self.on_cmd_sent)
        protocol.setAction(atprotocol.ON_CMD_RESULT, self.on_cmd_result)
        protocol.setAction(atprotocol.ON_INCOMING_CALL, self.on_incoming_call)
        protocol.setAction(atprotocol.ON_END_CALL, self.on_end_call)
        protocol.setAction(atprotocol.ON_CALLER_NUMBER_RECIEVED, self.on_caller_number_recieved)
        protocol.setAction(atprotocol.ON_DTMF_RECIEVED, self.on_DTMF_recieved)
        protocol.setAction(atprotocol.ON_UNKNOWN_MSG, self.on_unknown_msg)
        
        self._protocol = protocol
        # тест связи
        try:
            protocol.cmdTest()
        except Exception as e:
            log.exception("cant test connection")
    
    def processMessage(self, msg):
        log.debug("process message {}".format(msg))
        self._protocol.processMessage(msg)
    
    def on_cmd_sent(self, cmd):
        log.debug("command {} sent".format(cmd))
    
    def on_cmd_result(self, cmd, result, test_result):
        log.debug("recieved result of {} with {}".format(cmd, result))

        
    def on_incoming_call(self):
        log.debug("incoming call")
        
        
    def on_end_call(self):
        log.debug("call ended")
        
    def on_caller_number_recieved(self, number):
        log.debug("caller number recieved {}".format(number))
        # тут уже отвечаем на вызов
        # инициируем оператора
        
        self._protocol.answerCall()
        
    def on_DTMF_recieved(self, symbol):
        log.debug("DTMF sybol recieved {}".format(symbol))
        
    def on_unknown_msg(self, message):
        log.debug("unknown message recieved {}".format(message))
    
    
    