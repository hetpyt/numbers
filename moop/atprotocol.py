#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#import loggingwrapper as log

# служебные символы
SYMBOL_CR = "\r" #13 \r
SYMBOL_LF = "\n" #10 \n
ARGUMENTS_SEPARATOR = ","
COMMAND_SEPARATOR = ":"
SYMBOL_ARG_QUOTE = '"'

# команды AT
CMD_PREFIX = "AT"
CMD_ANSWER_CALL = CMD_PREFIX + "A"
CMD_END_CALL = CMD_PREFIX + "H"
# команды управления DTMF
COMMANDS = {
    DTMF : {
        BASE = "+DDET",
        ENABLE = "=1"
    }
}
DTMF_BASE = "+DDET"
CMD_DTMF = CMD_PREFIX + DTMF_BASE
CMD_DTMF_ENABLE = CMD_DTMF + "=1"
CMD_DTMF_DISABLE = CMD_DTMF + "=0"
CMD_DTMF_READ = CMD_DTMF + "?"
# результаты выполнения комманд
RES_SUCCESS = ("OK",)
RES_FAIL = ("ERROR", "NO CARRIER")
# незатребованные результаты выполнения комманд (приходят по событию извне)
MSG_INCOMING_CALL = "RING"
MSG_CALLER_INFO = "+CLIP"
MSG_END_CALL = "NO CARRIER"
MSG_DTMF_RECIEVED = "+DTMF"
# конец строки
END_LINE = "\r"
# события
ON_CMD_SENT = 1
ON_CMD_RESULT = 2
ON_INCOMING_CALL = 3
ON_END_CALL = 4
ON_CALLER_NUMBER_RECIEVED = 5
ON_DTMF_RECIEVED = 6
ON_UNKNOWN_MSG = 20
ACTIONS = (ON_CMD_SENT, ON_CMD_RESULT, ON_INCOMING_CALL, ON_END_CALL, ON_CALLER_NUMBER_RECIEVED, ON_DTMF_RECIEVED, ON_UNKNOWN_MSG)

class ATProtocol:
    
    def __init__(self, serial_protocol):
        self._protocol = serial_protocol
        self._last_cmd = None
        self._last_cmd_success = True
        self._cmd_attempts_count = 0
        self._actions = {key : None for key in ACTIONS}
    
    def _clear_last_cmd(self):
        self._last_cmd = None
    
    def _set_last_cmd(self, cmd):
        self._last_cmd = cmd
        
    def _get_last_cmd(self, clear = False):
        res = self._last_cmd
        if clear:
            self._clear_last_cmd()
        return res
    
    def _resend_cmd(self):
        self.sendCmd(_get_last_cmd())
    
    def _callBack(self, action, *args, **kwargs):
        if self._actions[action]:
            self._actions[action](*args, **kwargs)
            
    def _parce_args(self, args):
        # убираем кавычки
        return args.strip().replace(SYMBOL_ARG_QUOTE + ARGUMENTS_SEPARATOR, ARGUMENTS_SEPARATOR).replace(ARGUMENTS_SEPARATOR + SYMBOL_ARG_QUOTE, ARGUMENTS_SEPARATOR).replace(SYMBOL_ARG_QUOTE, '').split(ARGUMENTS_SEPARATOR)
        
    def _parse_msg(self, msg):
        head, _, args = msg.strip().partition(COMMAND_SEPARATOR)
        ret_args = ()
        if args:
            ret_args = tuple(self._parce_args(args))
        return head.upper(), ret_args
    
    def processMessage(self, msg):
        head, args = self._parse_msg(msg)
        
        if self._last_cmd:
            is_ok = (head in RES_SUCCESS)
            if is_ok:
                # вызываем событие
                pass
            else:
                # повтор команды
                pass
            self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok)
        
        if head in RESULTS and self._last_cmd:
            # сообщение является результатом команды
            # определяем результат
            is_ok = (head == RES_SUCCESS)
            if is_ok:
                # вызываем событие
                pass
            else:
                # повтор команды
                pass
            self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok)
     
        else:
            # не было команды устройству - незатребованный результат
            if head == MSG_END_CALL:
                # завершение вызова на той стороне
                self._callBack(ON_END_CALL)
            elif head == MSG_INCOMING_CALL:
                # входящий вызов
                self._callBack(ON_INCOMING_CALL)
            elif head == MSG_CALLER_INFO:
                # входящий вызов
                self._callBack(ON_CALLER_NUMBER_RECIEVED, number = args[0])
            elif head == MSG_DTMF_RECIEVED:
                # получен символ
                self._callBack(ON_DTMF_RECIEVED, symbol = args[0])
            else:
                self._callBack(ON_UNKNOWN_MSG, message = msg)
            
    def sendCmd(self, cmd):
        try:
            if not cmd:
                raise Exception('empty command')
            self._protocol.write(cmd + END_LINE)
            self._callBack(ON_CMD_SENT)
        except Exception as e:
            raise Exception("can't send command '{}' to device".format(cmd)) from e
    
    def answerCall(self):
        cmd = CMD_ANSWER_CALL
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
    
    def endCall(self):
        cmd = CMD_END_CALL
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
    
    def enableDTMF(self):
        cmd = CMD_DTMF_ENABLE
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)

    def disableDTMF(self):
        cmd = CMD_DTMF_DISABLE
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
        
    def readDTMFMode(self):
        cmd = CMD_DTMF_READ
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
        
    def setAction(self, action, ref):
        if action in self._actions:
            self._actions[action] = ref;
            
    def clearAction(self, action):
        if action in self._actions:
            self._actions[action] = None;
