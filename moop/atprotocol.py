#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loggingwrapper as log

# служебные символы
SYMBOL_CR = "\r" #13 \r
SYMBOL_LF = "\n" #10 \n
ARGUMENTS_SEPARATOR = ","
COMMAND_SEPARATOR = ":"
SYMBOL_ARG_QUOTE = '"'

# стандартные результаты выполнения комманд
R_OK = "OK"
R_ERR = "ERROR"

# команды управления 
COMMANDS = {
    "TEST" : {
        "CMD" : "AT",
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : None
            }
        },
    "ANSWER_CALL" : {
        "CMD" : "ATA",
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : "NO CARRIER"
            }
        },
    "END_CALL" : {
        "CMD" : "ATH",
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : None
            }
        },
    "DTMF_ENABLE" : {
        "CMD" : "AT+DDET=1",
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : "ERROR"
            }
        },    
    "DTMF_DISABLE" : {
        "CMD" : "AT+DDET=0",
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : "ERROR"
            }
        },
    "DTMF_IS_ENABLED" : {
        "CMD" : "AT+DDET?",
        "RESPONSE" : {
            "HEAD" : "+DDTE",
            "PARAMS" : ("MODE", "INTERVAL", "REPORTMODE", "SSDET")
            },
        "RESULT" : {
            "SUCCESS" : "OK",
            "FAIL" : "ERROR"
            },
        "TEST" : {
            "PARAM" : "MODE",
            "VALUE" : "1"
            }
        }
    }
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
        # сохраняем объект для обмена данными с устройством
        self._protocol = serial_protocol
        # имя последней посланной команды согласно COMMANDS
        self._last_cmd = None
        # ответ последней посланной команды (сохраняется до получения результата и потом отправляется)
        # принимает значения истина или ложь
        self._last_cmd_test = None
        # события
        self._actions = {key : None for key in ACTIONS}
    
    def _clear_last_cmd(self):
        self._last_cmd = None
        
    def _clear_last_cmd_test(self):
        self._last_cmd_test = None
        
    def _set_last_cmd(self, cmd):
        self._last_cmd = cmd
        
    def _get_last_cmd(self, clear = False):
        res = self._last_cmd
        if clear:
            self._clear_last_cmd()
        return res
        
    def _get_last_cmd_test(self, clear = False):
        res = self._last_cmd_test
        if clear:
            self._clear_last_cmd_test()
        return res
    
    def _resend_cmd(self):
        self.sendCmd(_get_last_cmd())
    
    def _callBack(self, action, *args, **kwargs):
        if self._actions[action]:
            self._actions[action](*args, **kwargs)
            
    def _parse_args(self, args):
        # убираем кавычки
        return args.strip().replace(SYMBOL_ARG_QUOTE + ARGUMENTS_SEPARATOR, ARGUMENTS_SEPARATOR).replace(ARGUMENTS_SEPARATOR + SYMBOL_ARG_QUOTE, ARGUMENTS_SEPARATOR).replace(SYMBOL_ARG_QUOTE, '').split(ARGUMENTS_SEPARATOR)
        
    def _parse_msg(self, msg):
        head, _, args = msg.strip().partition(COMMAND_SEPARATOR)
        ret_args = ()
        if args:
            ret_args = tuple(self._parse_args(args))
        return head.upper(), ret_args
    
    # def processMessage(self, msg):
        # head, args = self._parse_msg(msg)
        
        # if self._last_cmd:
            # is_ok = (head in RES_SUCCESS)
            # if is_ok:
                # # вызываем событие
                # pass
            # else:
                # # повтор команды
                # pass
            # self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok)
        
        # if head in RESULTS and self._last_cmd:
            # # сообщение является результатом команды
            # # определяем результат
            # is_ok = (head == RES_SUCCESS)
            # if is_ok:
                # # вызываем событие
                # pass
            # else:
                # # повтор команды
                # pass
            # self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok)
     
        # else:
            # # не было команды устройству - незатребованный результат
            # if head == MSG_END_CALL:
                # # завершение вызова на той стороне
                # self._callBack(ON_END_CALL)
            # elif head == MSG_INCOMING_CALL:
                # # входящий вызов
                # self._callBack(ON_INCOMING_CALL)
            # elif head == MSG_CALLER_INFO:
                # # входящий вызов
                # self._callBack(ON_CALLER_NUMBER_RECIEVED, number = args[0])
            # elif head == MSG_DTMF_RECIEVED:
                # # получен символ
                # self._callBack(ON_DTMF_RECIEVED, symbol = args[0])
            # else:
                # self._callBack(ON_UNKNOWN_MSG, message = msg)

    def processMessage(self, msg):
        head, args = self._parse_msg(msg)
        # получаем имя последней отправленной команды
        lc = self._get_last_cmd()
        if lc:
            # была отправлена команда - ожидаемо что это результат ее выполнения
            if head in COMMANDS[lc]["RESULT"].values():
                # результат выполнения команды
                is_ok = (head == COMMANDS[lc]["RESULT"]["SUCCESS"])
                # вызываем событие при этом забываем последнюю команду
                self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok, test_result = self._get_last_cmd_test(True))

            elif "RESPONSE" in COMMANDS[lc] and head == COMMANDS[lc]["RESPONSE"]["HEAD"]:
                # команда возращает ответ
                try:
                    self._last_cmd_test = (args[COMMANDS[lc]["RESPONSE"]["PARAMS"].index(COMMANDS[lc]["TEST"]["PARAM"])] == COMMANDS[lc]["TEST"]["VALUE"])
                except IndexError as e:
                    raise Exception("unexpected params count returned by command {}".format(lc))
            else:
                # вернулась какая то дичь
                raise Exception("unexpected result of command {}".format(lc))
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
            cmd_line = COMMANDS[cmd]["CMD"] + END_LINE
            self._protocol.write(cmd_line.encode())
            self._callBack(ON_CMD_SENT, cmd = cmd)
        except Exception as e:
            raise Exception("can't send command '{}' to device".format(cmd)) from e
    
    def cmdTest(self):
        cmd = "TEST"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
    
    def cmdAnswerCall(self):
        cmd = "ANSWER_CALL"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
    
    def cmdEndCall(self):
        cmd = "END_CALL"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
    
    def cmdEnableDTMF(self):
        cmd = "DTMF_ENABLE"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)

    def cmdDisableDTMF(self):
        cmd = "DTMF_DISABLE"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
        
    def cmdIsDTMFenabled(self):
        cmd = "DTMF_IS_ENABLED"
        self.sendCmd(cmd)
        self._set_last_cmd(cmd)
        
    def setAction(self, action, ref):
        if action in self._actions:
            self._actions[action] = ref;
            
    def clearAction(self, action):
        if action in self._actions:
            self._actions[action] = None;