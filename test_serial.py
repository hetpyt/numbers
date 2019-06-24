#!/usr/bin/env python
# -*- coding: utf-8 -*-
from serial import Serial
from serial.threaded import ReaderThread, LineReader
from serial.serialutil import SerialException
from queue import Queue, Empty
from time import clock, sleep as sys_sleep
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
        self.transport = transport
        transport.serial.rts = False
        self._lines = Queue()
        print('connection_made')


    def connection_lost(self, exc):
        print('connection_lost')
        if exc:
            #pass
    
    def handle_line(self, line):
        self._lines.put(line)
        #print(line)

    def is_empty(self):
        return self._lines.empty()
        
    def get_line(self):
        return self._lines.get_nowait()
        
def create_com_reader_thread(port, baudrate = 9600, protocol = None):
    ser_thread = MyReaderThread(port, baudrate, protocol)
    ser_thread.start()
    transport, instance = ser_thread.connect()
    return ser_thread, transport, instance

def is_alive(thread):
    if isinstance(thread, ReaderThread):
        return thread.is_alive()
    else:
        return False
        
if __name__ == '__main__':
    port = 'COM5'
    baudrate = 9600
    
    counter = 0
    ser_thread = None
    # main loop
    while True:
        if is_alive(ser_thread):
            # цикл ридера жив - можно работать
            if randint(0, 10) >= 5:
                data = 'counter = {}'.format(counter)
                print('sent: {}'.format(data))
                try:
                    instance.write_line(data)
                except Exception as e:
                    print("can't write: {}".format(e))
            try:
                print('recieved: {}'.format(instance.get_line()))
            except Empty as e:
                print('empty: {}'.format(e))
        else:
            # цикл ридера мертв - нужно (пере)запустить
            print('thread is dead - create')
            try:
                ser_thread, transport, instance = create_com_reader_thread(port, baudrate, MyLineReader)
            except Exception as e:
                print("can't create thread: {}".format(e))

        counter += 1
        sys_sleep(0.01)
    print('end')