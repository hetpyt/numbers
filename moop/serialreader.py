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
        try:
            com.open()
        except SerialException as e:
            raise Exception("can't open port '{}':{}".format(port, e)) from e
        super(MyReaderThread, self).__init__(com, protocol)

class SerialLineReader(LineReader):
    TERMINATOR = b'\n'
    def connection_made(self, transport):
        super(MyLineReader, self).connection_made(transport)
        transport.serial.rts = False
        self._lines = FilteredQueue()
        
    def connection_lost(self, exc):
        pass
    
    def handle_line(self, line):
        self._lines.put(line)

    # methods below called from another thread
    def get_count(self):
        self._lines.join()
        size = self._lines.qsize()
        self._lines._task_done()
        return size
        
    def get_line(self):
        return self._lines.get()
