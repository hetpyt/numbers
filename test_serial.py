#!/usr/bin/env python
# -*- coding: utf-8 -*-
from serial import Serial
from serial.threaded import ReaderThread, LineReader
from serial.serialutil import SerialException
from queue import Queue, Empty
from time import sleep as sys_sleep
# debug
from random import randint

class MyReaderThread(ReaderThread):
    def __init__(self, port, baudrate, protocol):
        com = Serial()
        com.port = port
        com.baudrate = baudrate
        com.bytesize = 8
        com.parity = 'N'
        try:
            com.open()
        except SerialException as e:
            raise Exception("can't open port '{}':{}".format(port, e)) from e
        super(MyReaderThread, self).__init__(com, protocol)

class MyLineReader(LineReader):
    TERMINATOR = b'\n'
    def connection_made(self, transport):
        super(MyLineReader, self).connection_made(transport)
        transport.serial.rts = False
        self._lines = Queue()
        print('connection_made')

    def connection_lost(self, exc):
        print('connection_lost')
    
    def handle_line(self, line):
        self._lines.put(line)
        #print(line)

    def is_empty(self):
        return self._lines.empty()
        
    def get_line(self):
        return self._lines.get_nowait()
        
if __name__ == '__main__':
    port = 'COM5'
    baudrate = 9600
    
    counter = 0
    ser_thread = None
    instance = None
    # main loop
    while True:
        # проверяем нить ридера
        if (ser_thread == None) or (not ser_thread.is_alive()):
            # нить ридера не существует или мертва - нужно (пере)запустить
            print('thread is dead')
            # перезупускаем когда вычитаем все строки из текущего ридера
            if (instance == None) or (instance.is_empty()):
                # текущий ридек не существует или пуст
                print('create thread')
                try:
                    ser_thread = MyReaderThread(port, baudrate, MyLineReader)
                    ser_thread.start()
                    _, instance = ser_thread.connect()
                except Exception as e:
                    print("can't create thread: {}".format(e))
        # делаем полезную работу
        # пишем в порт
        if instance:
            if randint(0, 10) >= 5:
                data = 'counter = {}'.format(counter)
                print('sent: {}'.format(data))
                try:
                    instance.write_line(data)
                except Exception as e:
                    print("can't write: {}".format(e))
            # читаем из порта строку если есть
            try:
                print('recieved: {}'.format(instance.get_line()))
            except Empty as e:
                print('empty: {}'.format(e))

        # задержка - убрать в проде
        counter += 1
        sys_sleep(1)
    print('end')