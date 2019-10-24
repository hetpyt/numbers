#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class AbstractStateMachine:
    def __init__(self, def_state = None):
        self._def_state = def_state
        self._state = def_state
        self._prev_state = None
        
    def _set_state(self, state):
        if self._state == state:
            # если новое состояние равно текущему, то ничего не делаем
            return
        self._prev_state = self._state
        self._state = state
        
    def _set_def_state(self):
        self._set_state(self._def_state)
        
    def _get_state(self):
        return self._state
        
    def _get_def_state(self):
        return self._def_state
        
    def _get_prev_state(self):
        return self._prev_state    
    
    def _reset_state(self):
        self._state = self._def_state
        self._prev_state = None

        