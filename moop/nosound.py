#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
from time import sleep
from threading import Thread
import loggingwrapper as log

class SleepingThread(Thread):
    def __init__(self, gain):
        self.gain = gain
        super(SleepingThread, self).__init__()
        
    def run(self):
        t = 3 * self.gain
        log.debug("sleeping on {} sec...".format(t))
        sleep(t)
        log.debug("awaiked...".format(t))

class PlayObj():
    def __init__(self, gain):
        self._thread = SleepingThread(gain)
        self._thread.start()
        
    def wait_done(self):
        log.debug('waiting for playing is complete')
        self._thread.join()

    def is_playing(self):
        if self._thread:
            return self._thread.is_alive()
        else:
            return False
        
    def stop(self):
        log.debug('waiting for playing is complete')
        self._thread = None
        

def play_buffer(data, nc, bps, fr):
    log.debug('begin playing sound...')
    return PlayObj()
    
def stop_all():
    log.debug('stop playing all sound')