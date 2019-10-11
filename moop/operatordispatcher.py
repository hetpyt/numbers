#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import atprotocol
from operator import Operator

# получает сообщения от устройства связи и обрабатывает их управляя экземляром класс Operator 
class OperatorDispatcher:
    
    def __init__():
        self._last_cmd = ""
        pass
    
    def init_protocol(serial_protocol):
        # инициирует протокол обмена с устройством связи
        self._protocol = atprotocol.ATProtocol(serial_protocol)
    
    def process_message(msg):
        is_cmd_exec_result = False
        if msg.upper() in []:
            is_at = True
        
        