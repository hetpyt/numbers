#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from globals import __MAIN_LOOP_DELAY__
import loggingwrapper as log
from serialreader import SerialReaderThread, SerialLineReader
# служебные символы
SYMBOL_CR = "\r" #13 \r
SYMBOL_LF = "\n" #10 \n
ARGUMENTS_SEPARATOR = ","
COMMAND_SEPARATOR = ":"
SYMBOL_ARG_QUOTE = '"'

# стандартные результаты выполнения комманд
R_OK = "OK"
R_ERR = "ERROR"
R_NOCR = "NO CARRIER"
CMD_TIMEOUT = int(120 / __MAIN_LOOP_DELAY__) # 30 sec

# команды управления 
COMMANDS = {
    "TEST" : {
        "CMD" : "AT",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : None
            }
        },
    "ANSWER_CALL" : {
        "CMD" : "ATA",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_NOCR
            }
        },
    "END_CALL" : {
        "CMD" : "ATH",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : None
            }
        },
    "DTMF_ENABLE" : {
        "CMD" : "AT+DDET=1",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        },    
    "DTMF_DISABLE" : {
        "CMD" : "AT+DDET=0",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        },
    "DTMF_IS_ENABLED" : {
        "CMD" : "AT+DDET?",
        "RESPONSE" : {
            "HEAD" : "+DDTE",
            "PARAMS" : ("MODE", "INTERVAL", "REPORTMODE", "SSDET")
            },
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
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
MSG_END_CALL = R_NOCR
MSG_DTMF_RECIEVED = "+DTMF"

# конец строки
END_LINE = SYMBOL_CR

# события
# возникает каждые __MAIN_LOOP_DELAY__ секунд
ON_TICK = 0
# возникает после отправки команды на устройство
ON_CMD_SENT = 1
# возникает при получении результата выполнения команды (OK, ERROR, etc)
ON_CMD_RESULT = 2
# возникает при получении от устройства сообщения о входящем вызове (RING)
ON_INCOMING_CALL = 3
# возникает при завершении вызова на той стороне (NO CARIER)
ON_END_CALL = 4
# возникает при получении сообщения определителя номера (+CLIP)
ON_CALLER_NUMBER_RECIEVED = 5
# возникает при получении сообщения содержащего код DTMF (+DTMF)
ON_DTMF_RECIEVED = 6
# возникает при ошибке отправки/получения данных с устройства
ON_PROTOCOL_ERROR = 18
# возникает при истечении времени ожидания результата команды (CMD_TIMEOUT)
ON_CMD_TIMEOUT = 19
# возникает при получении неизвестного незатребованного сообщения от устройства
ON_UNKNOWN_MSG = 20
# кортеж событий (содержит все события, которым можно назначить обработчик)
ACTIONS = (ON_TICK, ON_CMD_SENT, ON_CMD_RESULT, ON_INCOMING_CALL, ON_END_CALL, ON_CALLER_NUMBER_RECIEVED, ON_DTMF_RECIEVED, ON_PROTOCOL_ERROR, ON_CMD_TIMEOUT, ON_UNKNOWN_MSG)

class ATProtocol:
    
    def __init__(self, com_port, com_baudrate):
        self._com_port = com_port
        self._com_baudrate = com_baudrate
        self._ser_thread = None
        self._ser_reader = None
        # имя последней посланной команды согласно COMMANDS
        self._last_cmd = None
        # ответ последней посланной команды (сохраняется до получения результата и потом отправляется)
        # принимает значения истина или ложь
        self._last_test_result = None
        #
        self._last_cmd_timeout = None
        # события
        self._actions = {key : None for key in ACTIONS}
    
    def connect(self):
        try:
            self._ser_thread = SerialReaderThread(self._com_port, self._com_baudrate, SerialLineReader)
            self._ser_thread.start()
            _, self._ser_reader = self._ser_thread.connect()
            
        except Exception as e:
            log.exception("can't connect to serial device")
            self._callBack(ON_PROTOCOL_ERROR)
            #raise ATConnectionLostError("can't connect to serial device")
            
    def tick(self):
        if self._last_cmd:
            self._last_cmd_timeout -= 1
            if self._last_cmd_timeout <= 0:
                self._clear_cmd_timeout()
                self._callBack(ON_CMD_TIMEOUT, cmd = self._get_last_cmd(True))

        # проверяем нить ридера
        if (self._ser_thread == None) or (not self._ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            # перезупускаем когда вычитаем все строки из текущего ридера
            if (self._ser_reader == None) or (self._ser_reader.get_size() == 0):
                self.connect()
        # читаем строку если доступна
        if self._ser_reader and self._ser_reader.get_size():
            line = self._ser_reader.get_line()
            log.info("recieved message '{}'".format(line))
            self.processMessage(line)
            
        self._callBack(ON_TICK)
    
    def _clear_cmd_timeout(self):
        self._last_cmd_timeout = None
    
    def _set_cmd_timeout(self, ticks):
        self._last_cmd_timeout = ticks
    
    def _clear_last_cmd(self):
        self._last_cmd = None
        self._last_cmd_timeout = None
        
    def _set_last_cmd(self, cmd):
        self._last_cmd = cmd
        
    def _get_last_cmd(self, clear = False):
        res = self._last_cmd
        if clear:
            self._clear_last_cmd()
        return res
        
    def _clear_last_test_result(self):
        self._last_test_result = None
        
    def _set_last_test_result(self, res):
        self._last_test_result = res
    
    def _get_last_test_result(self, clear = False):
        res = self._last_test_result
        if clear:
            self._clear_last_test_result()
        return res
    
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
        
    def _sendCmd(self, cmd):
        try:
            # # проверки
            # if not cmd:
                # raise Exception("empty command")
            # if not cmd in COMMANDS:
                # raise Exception("not supported command '{}'".format(cmd))
            # формирование команды устройству
            cmd_line = COMMANDS[cmd]["CMD"] + END_LINE
            # сброс таймаута и служебных полей
            self._set_cmd_timeout(CMD_TIMEOUT)
            self._set_last_cmd(cmd)
            # отправка команды
            self._ser_thread.write(cmd_line.encode())
            # вызов события
            self._callBack(ON_CMD_SENT, cmd = cmd)
            
        except Exception as e:
            log.Exception("can't send command '{}' to device".format(cmd))
            self._callBack(ON_PROTOCOL_ERROR)
            
    def processMessage(self, msg):
        head, args = self._parse_msg(msg)
        # получаем имя последней отправленной команды
        lc = self._get_last_cmd()
        if lc:
            # была отправлена команда - ожидаемо что это результат ее выполнения
            if COMMANDS[lc]["CMD"] == msg:
                # включен режим эхо. устройство отправляет полученную команду обратно перед отправкой ответа
                pass
                
            elif head in COMMANDS[lc]["RESULT"].values():
                # результат выполнения команды
                is_ok = (head == COMMANDS[lc]["RESULT"]["SUCCESS"])
                # вызываем событие при этом забываем последнюю команду
                self._callBack(ON_CMD_RESULT, cmd = self._get_last_cmd(True), result = is_ok, test_result = self._get_last_test_result(True))

            elif "RESPONSE" in COMMANDS[lc] and head == COMMANDS[lc]["RESPONSE"]["HEAD"]:
                # команда возращает ответ
                try:
                    self._set_last_test_result(args[COMMANDS[lc]["RESPONSE"]["PARAMS"].index(COMMANDS[lc]["TEST"]["PARAM"])] == COMMANDS[lc]["TEST"]["VALUE"])
                except IndexError as e:
                    #raise Exception("unexpected params count returned by command {}".format(lc))
                    log.Exception("unexpected params count returned by command {}".format(lc))
                    self._callBack(ON_PROTOCOL_ERROR)

            else:
                # вернулась какая то дичь
                #raise Exception("unexpected result of command {}".format(lc))
                log.Exception("unexpected result {} of command {}".format(msg, lc))
                self._callBack(ON_PROTOCOL_ERROR)
                
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

    def resendCmd(self):
        lc = self._get_last_cmd()
        if lc:
            _sendCmd(lc)
            
    def cmdTest(self):
        cmd = "TEST"
        self._sendCmd(cmd)
    
    def cmdAnswerCall(self):
        cmd = "ANSWER_CALL"
        self._sendCmd(cmd)
    
    def cmdEndCall(self):
        cmd = "END_CALL"
        self._sendCmd(cmd)
    
    def cmdEnableDTMF(self):
        cmd = "DTMF_ENABLE"
        self._sendCmd(cmd)

    def cmdDisableDTMF(self):
        cmd = "DTMF_DISABLE"
        self._sendCmd(cmd)
        
    def cmdIsDTMFenabled(self):
        cmd = "DTMF_IS_ENABLED"
        self._sendCmd(cmd)
        
    def setAction(self, action, ref):
        if action in self._actions:
            self._actions[action] = ref;
            
    def clearAction(self, action):
        if action in self._actions:
            self._actions[action] = None;
