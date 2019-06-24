#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

class ConfigReader(dict):
    """read configuration from file"""
    def __init__(self, file_name):
        super(ConfigReader, self).__init__()
        self.__file_name = file_name
        # читаем файл
        self.read()
    
    def __str__(self):
        res = ''
        for key in super(ConfigReader, self).__iter__():
            res += key + '=' + str(super(ConfigReader, self).get(key)) + os.linesep
        return res
    
    def read(self):
        # открываем файл на чтение
        try:
            file = open(self.__file_name, "r", newline = os.linesep)
        except Exception as e:
            raise Exception("Can't open config file.") from e
        
        try:
            # цикл по строкам файла
            for line in file:
                line = line.strip()
                if (not line) or line[0] in '#;/':
                    continue
                key, value = tuple([s.strip() for s in line.split('=')])
                super(ConfigReader, self).__setitem__(key, value)

        except ValueError as e:
            raise Exception("config syntax error at'" + line + "'" ) from e
            
        finally:
            file.close()
            del file
