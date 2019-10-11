#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loggingwrapper as log
# служебные символы
ARGIMENTS_SEPARATOR = ","
COMMAND_SEPARATOR = ":"
# результаты выполнения комманд
COMMAND_SUCCESS_RES = "OK"
COMMAND_FAIL_RES = "ERROR"
COMMAND_NOCARRIER_RES = "NO CARRIER"
COMMAND_RESULTS = (COMMAND_SUCCESS_RES, COMMAND_FAIL_RES, COMMAND_NOCARRIER_RES)
# незатребованные результаты выполнения комманд (приходят по событию извне)
MSG_INCOMING_CALL = "RING"
MSG_CALL_WAITING_RES = "+CCWA"

END_LINE = "\r"

class ATProtocol:
    # Unsolicited results
    SUPPORTED_MESSAGES = {
        "RING" : {
            "ACTION" : None
            "PARAMS" : ()
        },
        "+CCWA" : {
            "ACTION" : None
            "PARAMS" : ("NUMBER", "TYPE", "CLASS")
            
        }
    }
    ON_CMD_SENT = 1
    ON_CMD_RESULT = 2
    ACTIONS = (ON_CMD_SENT, ON_CMD_RESULT)
    
    def __init__(self, serial_protocol):
        self._protocol = serial_protocol
        self._last_cmd = ""
        self._actions = {key : None for key in ACTIONS}
    
    def _callBack(self, action, *args, **kwargs):
        if self._actions[action]:
            self._actions[action](*args, **kwargs)
        
    def parseMessage(self, msg):
        if self._last_cmd:
            # была отправлена конманда устройству
            if msg in COMMAND_RESULTS:
                # сообщение является результатом команды
                is_ok = (msg == COMMAND_SUCCESS_RES)
                self._callBack("on_cmd_result") 
                pass
    
    def sendCmd(self, cmd):
        try:
            self._protocol.write(cmd + END_LINE)
        except Exception as e:
            raise Exception("can't send command '{}' to device".format(cmd)) from e
    
    def answerCall():
        cmd = "ATA"
        self.sendCmd(cmd)
        self._last_cmd = cmd
    
    def endCall():
        cmd = "ATH"
        self.sendCmd(cmd)
        self._last_cmd = cmd
        
    def setAction(self, action, ref):
        if action in self._actions:
            self._actions[action] = ref;
            
    def unsetAction(self, action):
        if action in self._actions:
            self._actions[action] = None;
