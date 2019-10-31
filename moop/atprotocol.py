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
# максимальная время ожидания ответа от устройства
CMD_TIMEOUT = int(30 / __MAIN_LOOP_DELAY__) # 30 sec
# задержка между попытками подключения к устройству
СONN_ATTEMTS_TIMEOUT = int(5 / __MAIN_LOOP_DELAY__) # 5 sec
# команды управления 
COMMANDS = {
    # тест связи
    "TEST" : {
        "CMD" : "AT",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : None
            }
        },
    # ответ на входящий вызов    
    "ANSWER_CALL" : {
        "CMD" : "ATA",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_NOCR
            }
        },
    # завершение вызова
    "END_CALL" : {
        "CMD" : "ATH",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : None
            }
        },
    # включение приема символов посредством DTMF
    "DTMF_ENABLE" : {
        "CMD" : "AT+DDET=1",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        },    
    # выключение приема символов посредством DTMF
    "DTMF_DISABLE" : {
        "CMD" : "AT+DDET=0",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        },
    # проверка включения приема символов посредством DTMF
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
            "VALUE" : ("1",)
            }
        },
    # включение АОН    
    "AON_ENABLE" : {
        "CMD" : "AT+CLIP=1",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        },   
    # отключение автоматического ответа на входящий вызов    
    "AUTOANSWER_DISABLE" : {
        "CMD" : "ATS0=0",
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            }
        }, 
    # проверка регистрации в домашней сети оператора    
    "CELL_IS_REGISTERED" : {
        "CMD" : "AT+CREG?",
        "RESPONSE" : {
            "HEAD" : "+CREG",
            "PARAMS" : ("NUM", "STAT")
            },
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            },
        "TEST" : {
            "PARAM" : "STAT",
            "VALUE" : ("1",)
            }
        },
    # проверка состояние модуля связи   
    "MODULE_IS_READY" : {
        "CMD" : "AT+CPAS",
        "RESPONSE" : {
            "HEAD" : "+CPAS",
            "PARAMS" : ("PAS")
            },
        "RESULT" : {
            "SUCCESS" : R_OK,
            "FAIL" : R_ERR
            },
        "TEST" : {
            "PARAM" : "PAS",
            "VALUE" : ("0", "3", "4")
            }
        }
    }
# незатребованные результаты выполнения комманд (приходят по событию извне)
# входящий вызов
MSG_INCOMING_CALL = "RING"
# информация АОН
MSG_CLIP_INFO = "+CLIP"
# разрыв связи
MSG_END_CALL = R_NOCR
# символ DTMF
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
# возникает при окончании выполнения последовательности команд
ON_CMD_SEQ_DONE = 9
# возникает при ошибке отправки/получения данных с устройства
ON_PROTOCOL_ERROR = 18
# возникает при истечении времени ожидания результата команды (CMD_TIMEOUT)
ON_CMD_TIMEOUT = 19
# возникает при получении неизвестного незатребованного сообщения от устройства
ON_UNKNOWN_MSG = 20
# кортеж событий (содержит все события, которым можно назначить обработчик)
ACTIONS = (ON_TICK, ON_CMD_SENT, ON_CMD_RESULT, ON_INCOMING_CALL, ON_END_CALL, ON_CALLER_NUMBER_RECIEVED, ON_DTMF_RECIEVED, ON_CMD_SEQ_DONE,
            ON_PROTOCOL_ERROR, ON_CMD_TIMEOUT, ON_UNKNOWN_MSG)

class ATProtocol:
    
    def __init__(self, com_port, com_baudrate):
        # флаг соединения с устройством
        self._connected = False
        # таимаут между попытками подключения
        self._conn_attemts_timeout = None
        # параметры устройства
        self._com_port = com_port
        self._com_baudrate = com_baudrate
        # объекты управления
        self._ser_thread = None
        self._ser_reader = None
        # итератор для перебора последовательности команд
        self._cmd_seq_iter = None
        # аккумулированный результат последовательности комманд (ложь если хоть одна команда возвратила ошибку)
        self._cmd_seq_result = None
        # имя последней посланной команды согласно COMMANDS
        self._last_cmd = None
        # ответ последней посланной команды (сохраняется до получения результата и потом отправляется)
        # принимает значения истина или ложь
        self._last_test_result = None
        #
        self._last_cmd_timeout = None
        # события
        self._actions = {key : None for key in ACTIONS}
    
    def _connect(self):
        
        if not self._conn_attemts_timeout == None:
            # включен таймаут переподключения
            self._conn_attemts_timeout -= 1
            if self._conn_attemts_timeout >= 0:
                # если время не вышло то выходим
                return
            
        try:
            self._ser_thread = SerialReaderThread(self._com_port, self._com_baudrate, SerialLineReader)
            self._ser_thread.start()
            _, self._ser_reader = self._ser_thread.connect()
            
            self._connected = True
            self._conn_attemts_timeout = None
            
        except Exception as e:
            log.exception("can't connect to serial device")
            log.info("retrying after {} ticks.".format(СONN_ATTEMTS_TIMEOUT))
            self._connected = False
            self._conn_attemts_timeout = СONN_ATTEMTS_TIMEOUT
            self._callBack(ON_PROTOCOL_ERROR)
            #raise ATConnectionLostError("can't connect to serial device")
            
    def _cmd_seq_begin(self, cmd_seq):
        self._cmd_seq_iter = iter(cmd_seq)
        self._cmd_seq_result = True
        self._cmd_seq_next()
    
    def _cmd_seq_end(self, over_res = None):
        sr = self._cmd_seq_result
        if not over_res == None:
            sr = over_res
        self._cmd_seq_iter = None
        self._cmd_seq_result = None
        self._callBack(ON_CMD_SEQ_DONE, result = sr)
    
    def _cmd_seq_next(self, res = None):
        # проверяем инициализирован ли итератор
        if not self._cmd_seq_iter:
            return
        if isinstance(res, bool):
            self._cmd_seq_result = self._cmd_seq_result and res
        # следующая команда    
        try:
            cmd = next(self._cmd_seq_iter)
            # отправка команды    
            self._sendCmd(cmd)
            
        except StopIteration as e:
            # команды последовательности закончились
            self._cmd_seq_end()
            
    def _is_cmd_seq(self):
        return (not self._cmd_seq_iter == None)
        
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
            # формирование команды устройству
            cmd_line = COMMANDS[cmd]["CMD"] + END_LINE
            # сброс таймаута и служебных полей
            self._set_cmd_timeout(CMD_TIMEOUT)
            self._set_last_cmd(cmd)
            # отправка команды
            self._ser_thread.write(cmd_line.encode())
            
        except Exception as e:
            log.exception("can't send command '{}' to device".format(cmd))
            self._callBack(ON_PROTOCOL_ERROR)
            
        # вызов события
        self._callBack(ON_CMD_SENT, cmd = cmd)
        
    def _process_message(self, msg):
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
                # обработка последовательностей команд
                if self._is_cmd_seq():
                    self._cmd_seq_next(is_ok)
                    
            elif "RESPONSE" in COMMANDS[lc] and head == COMMANDS[lc]["RESPONSE"]["HEAD"]:
                # команда возращает ответ
                try:
                    self._set_last_test_result(args[COMMANDS[lc]["RESPONSE"]["PARAMS"].index(COMMANDS[lc]["TEST"]["PARAM"])] in COMMANDS[lc]["TEST"]["VALUE"])
                except IndexError as e:
                    #raise Exception("unexpected params count returned by command {}".format(lc))
                    log.exception("unexpected params count returned by command {}".format(lc))
                    self._callBack(ON_PROTOCOL_ERROR)

            else:
                # вернулась какая то дичь
                #raise Exception("unexpected result of command {}".format(lc))
                log.error("unexpected result '{}' of command {}".format(msg, lc))
                self._callBack(ON_PROTOCOL_ERROR)
                # обработка последовательностей команд
                if self._is_cmd_seq():
                    self._cmd_seq_end(False)
        else:
            # не было команды устройству - незатребованный результат
            if head == MSG_END_CALL:
                # завершение вызова на той стороне
                self._callBack(ON_END_CALL)
            elif head == MSG_INCOMING_CALL:
                # входящий вызов
                self._callBack(ON_INCOMING_CALL)
            elif head == MSG_CLIP_INFO:
                # входящий вызов
                self._callBack(ON_CALLER_NUMBER_RECIEVED, number = args[0])
            elif head == MSG_DTMF_RECIEVED:
                # получен символ
                self._callBack(ON_DTMF_RECIEVED, symbol = args[0])
            else:
                self._callBack(ON_UNKNOWN_MSG, message = msg)
                
    def tick(self):
        if self._last_cmd:
            self._last_cmd_timeout -= 1
            if self._last_cmd_timeout <= 0:
                self._clear_cmd_timeout()
                # раз нет ответа значит нет связи
                self._connected = False 
                self._callBack(ON_CMD_TIMEOUT, cmd = self._get_last_cmd(True))
                # обработка последовательностей команд
                if self._is_cmd_seq():
                    self._cmd_seq_end(False)

        # проверяем нить ридера
        if (self._ser_thread == None) or (not self._ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            # перезупускаем когда вычитаем все строки из текущего ридера
            self._connected = False 
            if (self._ser_reader == None) or (self._ser_reader.get_size() == 0):
                self._connect()
        # читаем строку если доступна
        if self._ser_reader and self._ser_reader.get_size():
            line = self._ser_reader.get_line()
            log.info("recieved message '{}'".format(line))
            self._process_message(line)
            
        self._callBack(ON_TICK)
    
    def execCmdSeq(self, cmd_seq):
        self._cmd_seq_begin(cmd_seq)
    
    def sendCmd(self, cmd):
        # проверки
        if not cmd:
            raise Exception("empty command")
        if not cmd in COMMANDS:
            raise Exception("not supported command '{}'".format(cmd))
            
        self._sendCmd(cmd)
    
    def isReady(self):
        return self._connected
    
    def resendCmd(self):
        lc = self._get_last_cmd()
        if lc:
            _sendCmd(lc)

    def cmdRestart(self):
        cmd = "RESTART"
        #self._sendCmd(cmd)
    
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
    
    def cmdIsCellRegistered(self):
        cmd = "CELL_IS_REGISTERED"
        self._sendCmd(cmd)
    
    def cmdIsModuleReady(self):
        cmd = "MODULE_IS_READY"
        self._sendCmd(cmd)
        
    def setAction(self, action, ref):
        if action in self._actions:
            self._actions[action] = ref;
            
    def clearAction(self, action):
        if action in self._actions:
            self._actions[action] = None;
