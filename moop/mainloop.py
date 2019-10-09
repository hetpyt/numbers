#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from moop.serialreader import SerialReaderThread
from time import sleep as sys_sleep

if __name__ == '__main__':
    
    # preparation
    
    # reading config
    port = 'COM5'
    baudrate = 9600
    # globals
    counter = 0
    __ser_thread = None
    __ser_protocol = None
    # main loop
    while True:
        # проверяем нить ридера
        if (__ser_thread == None) or (not __ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            # перезупускаем когда вычитаем все строки из текущего ридера
            if (__ser_transport == None) or (__ser_transport.get_size() == 0):
                # текущий ридер не существует или пуст
                try:
                    __ser_thread = SerialReaderThread(port, baudrate, MyLineReader)
                    __ser_thread.start()
                    _, __ser_protocol = __ser_thread.connect()
                except Exception as e:
                    #print("can't create thread: {}".format(e))
                    pass
        # делаем полезную работу
        # пишем в порт
        if instance:
            # читаем из порта строку если есть
            try:
                __ser_protocol.get_line()
            except Empty as e:
                print('empty: {}'.format(e))

        # задержка - убрать в проде
        counter += 1
        sys_sleep(0.1)
    print('end')