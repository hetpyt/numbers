#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atprotocol
from operator import Operator

# получает сообщения от устройства связи и обрабатывает их управляя экземляром класс Operator 
class OperatorDispatcher:
    
    def __init__():
        self._online = False
        self._caller_number = None
        
        
    def _init_operator(self):
        pass
        
    def initProtocol(serial_protocol):
        # инициирует протокол обмена с устройством связи
        protocol = atprotocol.ATProtocol(serial_protocol)
        # установка событий
        protocol.setAction(atprotocol.ON_CMD_RESULT, self.on_cmd_result)
        protocol.setAction(atprotocol.ON_INCOMING_CALL, self.on_incoming_call)
        protocol.setAction(atprotocol.ON_END_CALL, self.on_end_call)
        protocol.setAction(atprotocol.ON_CALLER_NUMBER_RECIEVED, self.on_caller_number_recieved)
        protocol.setAction(atprotocol.ON_DTMF_RECIEVED, self.on_DTMF_recieved)
        protocol.setAction(atprotocol.ON_UNKNOWN_MSG, self.on_unknown_msg)
        
        self._protocol = protocol
    
    def processMessage(msg):
        self._protocol.processMessage(msg)
    
    def on_cmd_result(self, cmd, result):
        if cmd == operator.CMD_ANSWER_CALL:
            self._online = result
            if self._online:
                self._init_operator()
            
        elif cmd == operator.CMD_END_CALL:
            self._online = False
        
    def on_incoming_call(self):
        # ждем получения номер звонящего
        pass
        
    def on_end_call(self):
        pass
        
    def on_caller_number_recieved(self, number):
        # тут уже отвечаем на вызов
        # инициируем оператора
        
        self._protocol.answerCall()
        
        
    def on_DTMF_recieved(self):
        pass
        
    def on_unknown_msg(self):
        pass
    
    
    