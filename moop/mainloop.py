#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from sys import exit
import loggingwrapper as log
from serialreader import SerialReaderThread, SerialLineReader
from configreader import ConfigReader
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
    __counter = 0
    __ser_thread = None
    __ser_protocol = None
    __dispatcher = OperatorDispatcher()
    # main loop
    __log.debug("main loop started")
    while True:
        # проверяем нить ридера
        if (__ser_thread == None) or (not __ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            # перезупускаем когда вычитаем все строки из текущего ридера
            if (__ser_protocol == None) or (__ser_protocol.get_size() == 0):
                # текущий ридер не существует или пуст
                try:
                    __ser_thread = SerialReaderThread(__config["com_port"], __config["com_baudrate"], SerialLineReader)
                    __ser_thread.start()
                    transport, __ser_protocol = __ser_thread.connect()
                    #print(transport)
                    #print(__ser_protocol)
                except Exception as e:
                    __log.exception("can't create thread")
                    #print("can't create thread: {}".format(e))
                    __log.info("retry after 10 seconds...")
                    sleep(10)
        # делаем полезную работу
        if __ser_protocol and __ser_protocol.get_size():
            line = __ser_protocol.get_line()
            __log.info("recieved message '{}'".format(line))
            __dispatcher.process_message(line)
            
        # задержка 
        __counter += 1
        #print("main loop {}".format(__counter))
        sleep(0.1)
    #print('end')