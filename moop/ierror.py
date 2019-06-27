#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class IError():
    def __init__(self):
        #print('IError __init__')
        self.reset_error()
        super().__init__()
        
    def _set_error(self, text):
        self._error = True
        self._error_text = text
        
    def is_error(self):
        return self._error
    
    def get_error(self):
        return self._error_text
        
    def set_error(self, error_text):
        self._error = True
        self._error_text = error_text
        
    def reset_error(self):
        self._error_text = ''
        self._error = False
