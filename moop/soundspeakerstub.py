#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import loggingwrapper as log
from numberspeaker import NumberSpeaker
import nosound as SA

SOUNDS = ()

class SoundSpeaker(NumberSpeaker):
    """speak the sequence"""
    def __init__(self, resource_path):
        self._play_obj = None
        self._res_path = resource_path
        super(SoundSpeaker, self).__init__()

    def speak(self, sequence):
        gain = 0
        for word in sequence:
            if word[:4] == 'std_':
                gain += 1 
        log.debug("begin playing {}".format(sequence))
        try:
            self._play_obj = SA.PlayObj(gain)
        except Exception as e:
            raise Exception("can't play sound") from e
    
    def speakAndWait(self, sequence):
        self.speak(sequence)
        if self.isSpeaking():
            self._play_obj.wait_done()
    
    def isSpeaking(self):
        if self._play_obj:
            return self._play_obj.is_playing()
        else:
            return False
    
    def stop(self):
        if self.isSpeaking():
            self._play_obj.stop()
        self._play_obj = None
            
    @staticmethod
    def stopAll():
        SA.stop_all()
