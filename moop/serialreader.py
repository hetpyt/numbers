#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from serial import Serial
from serial.threaded import ReaderThread, LineReader
from serial.serialutil import SerialException
from queue import Queue, Empty
from filteredqueue import FilteredQueue

class SerialReaderThread(ReaderThread):
    def __init__(self, port, baudrate, protocol):
        com = Serial()
        com.port = port
        com.baudrate = baudrate
        com.bytesize = 8
        com.parity = 'N'
        com.open()
        super(SerialReaderThread, self).__init__(com, protocol)

def create_thread(port, baudrate, protocol):
    com = Serial()
    com.port = port
    com.baudrate = baudrate
    com.bytesize = 8
    com.parity = 'N'
    com.open()
    return ReaderThread(com, protocol)

class SerialLineReader(LineReader):
    TERMINATOR = b'\r'
    def connection_made(self, transport):
        print("connetction made")
        transport.serial.rts = False
        self._transport = transport
        self._lines = FilteredQueue()
        super(SerialLineReader, self).connection_made(transport)
        
    def connection_lost(self, exc):
        print("connection_lost")
        print(self._transport)
    
    def handle_line(self, line):
        print("handle line '{}'".format(line))
        self._lines.put(line)
        print("handle line2")

    # methods below called from another thread
    def get_size(self):
        self._lines.join()
        size = self._lines.qsize()
        #self._lines.task_done()
        return size
        
    def get_line(self):
        try:
            return self._lines.get(False)
        except Empty as e:
            return None
