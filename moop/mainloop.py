#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from sys import exit
from globals import __MAIN_LOOP_DELAY__
import loggingwrapper as log
from aterror import ATConnectionLostError
from configreader import ConfigReader
from atprotocol import ATProtocol
from operatordispatcher import OperatorDispatcher

    

if __name__ == '__main__':
    
    # preparation
    __log = log.create_log("moop.log", log.DEBUG)
    
    # reading config
    try:
        __config = ConfigReader("moop.cfg")
    except Exception as e:
        __log.critical("config not loaded: {}".format(e))
        exit(1)
    
    if not __config.is_readed():
        __log.critical("no config file was found")
        exit(1)
    # проверка параметров подключения к устройству
    if not __config.is_params_exists(("com_port", "com_baudrate")):
        __log.critical("serial communication parameters not completely defined in config file '{}'".format(__config.get_file_name()))
        exit(1)
    # проверка параметров подключения к субд
    if not __config.is_params_exists(("db_type", "db_server", "db_port", "db_name", "db_user", "db_pass")):
        __log.critical("database connection parameters not completely defined in config file '{}'".format(__config.get_file_name()))
        exit(1)
    # проверка параметров воспроизведения звука
    if not __config.is_params_exists(("sp_resource_path", "sp_error_message", "sp_greeting_message", "sp_noacc_message",
            "sp_acc_selection1", "sp_acc_selection2", "sp_mtr_question1", "sp_mtr_question2", "sp_mtr_question2", "sp_mtr_newvalue",
            "sp_mtr_confirmation1", "sp_mtr_confirmation2", "sp_mtr_confirmation3", "sp_farewell_message")):
        __log.critical("sound play parameters not completely defined in config file '{}'".format(__config.get_file_name()))
        exit(1)
    # globals
    # протокол обмена сообщениями с устройством связи
    __protocol = ATProtocol(__config["com_port"], __config["com_baudrate"])
    # диспетчер для управления устройством связи и оператором
    __dispatcher = OperatorDispatcher(__config)
    # инициализация протокола в диспетчере
    __dispatcher.initProtocol(__protocol)
    # main loop
    __log.debug("main loop started")
    while True:
        # дергаем протокол
        try:
            __protocol.tick()
        except ATConnectionLostError as e:
            __log.exception("can't create thread")
            __log.info("retry after 10 seconds")
            sleep(10)
        except Exception as e:
            __log.exception("something goes wrong")
        
        # задержка 
        sleep(__MAIN_LOOP_DELAY__)
    #print('end')