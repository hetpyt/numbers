#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import loggingwrapper as log
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

ON_CMD_SENT = 1
ON_CMD_RESULT = 2
ON_INCOMING_CALL = 3
ON_CALLER_NUMBER_RECIEVED = 4

ACTIONS = (ON_CMD_SENT, ON_CMD_RESULT, ON_INCOMING_CALL, ON_CALLER_NUMBER_RECIEVED)

class ATProtocol:
    
    def __init__(self, serial_protocol):
        self._protocol = serial_protocol
        self._last_cmd = ""
        self._actions = {key : None for key in ACTIONS}
    
    def _callBack(self, action, *args, **kwargs):
        if self._actions[action]:
            self._actions[action](*args, **kwargs)
        
    def parseMessage(self, msg):
        if msg in COMMAND_RESULTS:
            # сообщение является результатом команды
            if self._last_cmd:
                # была отправлена конманда устройству
                is_ok = (msg == COMMAND_SUCCESS_RES)
                self._callBack(ON_CMD_RESULT)
            else:
                # не было команды устройству
        else:
            # нет команды - сообщение не затребовано
            
    def sendCmd(self, cmd):
        try:
            self._protocol.write(cmd + END_LINE)
            self._callBack(ON_CMD_SENT)
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
