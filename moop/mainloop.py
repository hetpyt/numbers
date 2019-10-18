#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from sys import exit
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
    
    if not __config.is_params_exists(("com_port", "com_baudrate")):
        __log.critical("serial communication parameters not defined in config file '{}'".format(__config.get_file_name()))
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
        sleep(0.1)
    #print('end')