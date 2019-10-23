#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import sleep
import loggingwrapper as log

class PlayObj():
    def __init__(self):
        self._is_playing = True
        
    def wait_done(self):
        log.debug('waiting for playing is complete')
        sleep(3)
        self._is_playing = False

        
    def is_playing(self):
        return self._is_playing
        
    def stop():
        self._is_playing = False
        

def play_buffer(data, nc, bps, fr):
    log.debug('begin playing sound...')
    return PlayObj()
    
def stop_all():
    log.debug('stop playing all sound')