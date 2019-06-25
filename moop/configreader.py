#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from moop.ierror import IError

class ConfigReader(IError, dict):
    """read configuration from file"""
    def __init__(self, file_name):
        super().__init__()
        self._file_name = file_name
        # читаем файл
        self.read()
    
    def __str__(self):
        res = ''
        for key in self:
            res += key + '=' + str(self.get(key)) + os.linesep
        return res
    
    def read(self):
        # открываем файл на чтение
        try:
            file = open(self._file_name, "r", newline = os.linesep)
        except Exception as e:
            self._set_error("Can't open config file '{}': {}".format(self._file_name, e))
            return
        
        try:
            # цикл по строкам файла
            line_counter = 0
            for line in file:
                line_counter += 1
                line = line.strip()
                if (not line) or line[0] in '#;/':
                    continue
                key, value = tuple([s.strip() for s in line.split('=')])
                self.__setitem__(key, value)

        except ValueError as e:
            self._set_error("config syntax error at line #{}: key=value required".format(line_counter))
            return
            
        finally:
            file.close()
            del file
