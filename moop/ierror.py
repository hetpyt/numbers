#!/usr/bin/env python
# -*- coding: utf-8 -*-

class IError():
    def __init__(self):
        self._error = False
        self._error_text = ''
        
    def _set_error(self, text):
        self._error = True
        self._error_text = text
        
    def is_error(self):
        return self._error
    
    def get_error(self):
        return self._error
        
    def set_error(self, error_text):
        self._error = True
        self._error_text = error_text
        
    def reset_error(self):
        error_text = self._error_text
        self._error_text = ''
        self._error = False
        return error_text