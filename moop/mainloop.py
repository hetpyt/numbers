#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from serialreader import create_thread, SerialLineReader
from configreader import ConfigReader
from time import sleep
from sys import exit

if __name__ == '__main__':
    
    # preparation
    
    # reading config
    try:
        __config = ConfigReader("moop.cfg")
    except Exception as e:
        exit("config not loaded: {}".format(e))
    
    if not __config.is_readed():
        exit("no config file was found")
    
    if __config.is_params_exists(("com_port", "com_baudrate")):
        __ser_port = __config["com_port"]
        __ser_baudrate = __config["com_baudrate"]
    else:
        exit("serial communication parameters not defined in config file '{}'".format(__config.get_file_name()))
        
    # globals
    __ser_thread = None
    __ser_protocol = None
    # main loop
    while True:
        # проверяем нить ридера
        if (__ser_thread == None) or (not __ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            # перезупускаем когда вычитаем все строки из текущего ридера
            if (__ser_protocol == None) or (__ser_protocol.get_size() == 0):
                # текущий ридер не существует или пуст
                try:
                    #__ser_thread = SerialReaderThread(__ser_port, __ser_baudrate, SerialLineReader)
                    __ser_thread = create_thread(__ser_port, __ser_baudrate, SerialLineReader)
                    __ser_thread.start()
                    transport, __ser_protocol = __ser_thread.connect()
                    print(transport)
                    print(__ser_protocol)
                except Exception as e:
                    print("can't create thread: {}".format(e))
                    print("retry after 10 seconds...")
                    sleep(10)
        # делаем полезную работу
        # пишем в порт
        if __ser_protocol and __ser_protocol.get_size():
            print("get_line")
            line = __ser_protocol.get_line()
            print(line)
            
        # задержка 
        #print("main loop")
        sleep(0.5)
    print('end')